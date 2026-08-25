from pathlib import Path
import re
import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS AND CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHROMA_PATH = (
    PROJECT_ROOT
    / "data"
    / "vector_db"
)

COLLECTION_NAME = "indian_constitution"

MODEL_NAME = "BAAI/bge-small-en-v1.5"


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Embedding model loaded.")


# ============================================================
# CONNECT TO CHROMADB
# ============================================================

client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

collection = client.get_collection(
    name=COLLECTION_NAME
)

print(
    f"Connected to collection: {COLLECTION_NAME}"
)

print(
    f"Total chunks: {collection.count()}"
)

def detect_article_number(query):

    pattern = r"\barticle\s+(\d+[A-Za-z]?)\b"

    match = re.search(
        pattern,
        query,
        flags=re.IGNORECASE
    )

    if match:
        return match.group(1).upper()

    return None

def expand_query(query):

    query_lower = query.lower()

    expansions = {
        "amend": (
            "constitutional amendment procedure "
            "Article 368 Parliament special majority"
        ),

        "constitution amended": (
            "constitutional amendment procedure "
            "Article 368 Parliament"
        ),

        "fundamental rights": (
            "Fundamental Rights Part III "
            "Articles 12 to 35"
        ),

        "right to education": (
            "Right to Education Article 21A "
            "free compulsory education children"
        ),

        "arrest": (
            "arrest detention rights Article 22 "
            "magistrate legal practitioner"
        ),

        "supreme court powers": (
            "Supreme Court jurisdiction powers "
            "Articles 32 136 137 138 139 140"
        )
    }

    expanded_query = query

    for keyword, expansion in expansions.items():

        if keyword in query_lower:

            expanded_query = (
                f"{query} {expansion}"
            )

            print(
                f"\nExpanded query: "
                f"{expanded_query}"
            )

            break

    return expanded_query


def get_complete_article(article_number):

    results = collection.get(
        where={
            "article_number": article_number
        },
        include=[
            "documents",
            "metadatas"
        ]
    )

    documents = results["documents"]
    metadatas = results["metadatas"]

    print(
        f"\nChunks found for Article {article_number}: "
        f"{len(documents)}"
    )
    
    for metadata in metadatas:
    
        print(
            f"Clause found: {metadata['clause']}"
        )
    combined = list(
        zip(
            documents,
            metadatas
        )
    )

    combined.sort(
        key=lambda item: (
            int(item[1]["clause"])
            if item[1]["clause"]
            else 0
        )
    )

    documents = [
        item[0]
        for item in combined
    ]

    metadatas = [
        item[1]
        for item in combined
    ]

    return {
        "documents": [documents],
        "metadatas": [metadatas],
        "distances": [
            [0.0] * len(documents)
        ]
    }
# ============================================================
# SEARCH FUNCTION
# ============================================================

def search_constitution(
    query,
    top_k=5
):

    article_number = detect_article_number(
        query
    )

    # ============================================================
    # EXACT ARTICLE SEARCH
    # ============================================================

    if article_number:

        print(
            f"\nDetected Article: {article_number}"
        )

        print(
            "Retrieving complete Article..."
        )

        return get_complete_article(
            article_number
        )

    # ============================================================
    # NORMAL SEMANTIC SEARCH
    # ============================================================

    search_query = expand_query(
        query
    )

    print(
        "\nCreating query embedding..."
    )

    query_embedding = model.encode(
        search_query,
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    # ============================================================
    # SMART ARTICLE EXPANSION
    # ============================================================

    top_metadata = results["metadatas"][0][0]

    top_article = top_metadata["article_number"]

    top_distance = results["distances"][0][0]

    print(
        f"\nTop relevant Article: {top_article}"
    )

    print(
        f"Top result distance: {top_distance:.4f}"
    )

    # Retrieve the complete article when the
    # semantic match is sufficiently strong.
    if top_distance < 0.50:

        print(
            f"Retrieving complete Article {top_article}..."
        )

        return get_complete_article(
            top_article
        )

    return results

# ============================================================
# BUILD RETRIEVAL CONTEXT
# ============================================================

def build_context(results):

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    context_parts = []

    for document, metadata in zip(
        documents,
        metadatas
    ):

        context_parts.append(
            f"""
                Article {metadata['article_number']}
                Title: {metadata['article_title']}
                Part: {metadata['part']}

            {document}""".strip()
        )

    context = "\n\n".join(
        context_parts
    )

    return context

# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(results):

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    distances = results["distances"][0]

    print("\n" + "=" * 70)
    print("SEARCH RESULTS")
    print("=" * 70)

    for index, (
        document,
        metadata,
        distance
    ) in enumerate(
        zip(
            documents,
            metadatas,
            distances
        ),
        start=1
    ):

        print(
            f"\nRESULT {index}"
        )

        print(
            f"Article: "
            f"{metadata['article_number']}"
        )

        print(
            f"Title: "
            f"{metadata['article_title']}"
        )

        print(
            f"Part: "
            f"{metadata['part']}"
        )

        print(
            f"Clause: "
            f"{metadata['clause']}"
        )

        print(
            f"Status: "
            f"{metadata['status']}"
        )

        print(
            f"Distance: "
            f"{distance:.4f}"
        )

        print("\nText:")

        print(document)

        print(
            "\n" + "-" * 70
        )



# ============================================================
# MAIN
# ============================================================

def main():

    while True:

        query = input(
            "\nAsk a question about the Constitution "
            "(or type 'exit'): "
        )
        

        if query.lower() == "exit":

            print(
                "\nExiting Samvidhaan AI search."
            )

            break

        results = search_constitution(
            query=query,
            top_k=5
        )

        context = build_context(
            results
        )

        print("\n" + "=" * 70)
        print("RETRIEVED CONTEXT")
        print("=" * 70)

        print(context)


if __name__ == "__main__":
    main()