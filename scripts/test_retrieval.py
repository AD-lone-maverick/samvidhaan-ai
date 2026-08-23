from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHROMA_PATH = (
    PROJECT_ROOT
    / "data"
    / "vector_db"
)

COLLECTION_NAME = "indian_constitution"


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

model = SentenceTransformer(
    "BAAI/bge-small-en-v1.5"
)

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


# ============================================================
# SEARCH FUNCTION
# ============================================================

def search_constitution(query, n_results=5):

    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    return results


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(results):

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    print("\n" + "=" * 70)
    print("RETRIEVAL RESULTS")
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
            f"Article: {metadata['article_number']}"
        )

        print(
            f"Title: {metadata['article_title']}"
        )

        print(
            f"Part: {metadata['part']}"
        )

        print(
            f"Clause: {metadata['clause']}"
        )

        print(
            f"Status: {metadata['status']}"
        )

        print(
            f"Distance: {distance:.4f}"
        )

        print("\nText:")

        print(document)

        print(
            "\n" + "-" * 70
        )


# ============================================================
# TEST QUERIES
# ============================================================

test_queries = [

    "What are my rights if I am arrested?",

    "What does the Constitution say about freedom of speech?",

    "How can a person become a citizen of India?",

    "What are the powers of the Gram Sabha?"
]


for query in test_queries:

    print("\n" + "#" * 70)

    print(
        f"QUERY: {query}"
    )

    print("#" * 70)

    results = search_constitution(
        query
    )

    display_results(
        results
    )


print("\n" + "=" * 70)
print("RETRIEVAL TEST COMPLETE")
print("=" * 70)