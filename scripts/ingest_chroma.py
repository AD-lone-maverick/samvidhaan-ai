from pathlib import Path
import json

import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHUNKS_PATH = (
    PROJECT_ROOT
    / "data"
    / "chunks"
    / "constitution_chunks.json"
)

CHROMA_PATH = (
    PROJECT_ROOT
    / "data"
    / "vector_db"
)

COLLECTION_NAME = "indian_constitution"


# ============================================================
# LOAD CHUNKS
# ============================================================

print("Loading Constitution chunks...")

with open(CHUNKS_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)

chunks = data["chunks"]

print(f"Chunks loaded: {len(chunks)}")


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

model = SentenceTransformer(
    "BAAI/bge-small-en-v1.5"
)

print("Embedding model loaded.")


# ============================================================
# CREATE CHROMA CLIENT
# ============================================================

client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)


# Delete old collection if it exists.
try:
    client.delete_collection(
        name=COLLECTION_NAME
    )
    print("Old collection deleted.")
except Exception:
    print("Creating new collection.")


collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)

# ============================================================
# METADATA CLEANING
# ============================================================

def clean_metadata(metadata):

    cleaned = {}

    for key, value in metadata.items():

        if value is None:
            cleaned[key] = ""

        elif isinstance(
            value,
            (str, int, float, bool)
        ):
            cleaned[key] = value

        else:
            cleaned[key] = str(value)

    return cleaned

# ============================================================
# PREPARE DATA
# ============================================================

documents = []
metadatas = []
ids = []


for chunk in chunks:

    chunk_id = chunk["chunk_id"]

    documents.append(
        chunk["text"]
    )

    metadata = {
        "article_number": chunk.get(
            "article_number"
        ),
        "article_title": chunk.get(
            "article_title"
        ),
        "part": chunk.get(
            "part"
        ),
        "part_title": chunk.get(
            "part_title"
        ),
        "status": chunk.get(
            "status"
        ),
        "clause": chunk.get(
            "clause"
        )
    }

    metadatas.append(
        clean_metadata(metadata)
    )

    ids.append(
        chunk_id
    )


print(
    f"Unique chunks prepared: {len(documents)}"
)





# ============================================================
# CREATE EMBEDDINGS
# ============================================================

print("Creating embeddings...")

embeddings = model.encode(
    documents,
    show_progress_bar=True,
    normalize_embeddings=True
).tolist()

print(
    f"Embeddings created: {len(embeddings)}"
)


# ============================================================
# STORE IN CHROMADB
# ============================================================

print("Storing embeddings in ChromaDB...")

BATCH_SIZE = 100

for start in range(
    0,
    len(documents),
    BATCH_SIZE
):

    end = min(
        start + BATCH_SIZE,
        len(documents)
    )

    collection.add(
        ids=ids[start:end],
        documents=documents[start:end],
        metadatas=metadatas[start:end],
        embeddings=embeddings[start:end]
    )

    print(
        f"Stored chunks {start} to {end}"
    )


# ============================================================
# VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("CHROMADB INGESTION COMPLETE")
print("=" * 60)

print(
    f"Total chunks in database: {collection.count()}"
)

print(
    f"Database location: {CHROMA_PATH}"
)