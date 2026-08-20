import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "constitution_clean.json"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "chunks"
    / "constitution_chunks.json"
)

def load_json(path):

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(data, path):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )

def remove_article_heading(text, article_number):

    pattern = (
        rf"^{re.escape(article_number)}\."
        rf".*?—"
    )

    cleaned = re.sub(
        pattern,
        "",
        text,
        count=1,
        flags=re.DOTALL
    )

    return cleaned.strip()

CLAUSE_PATTERN = re.compile(
    r"(?m)^\s*[*]*\((\d+)\)\s*"
)

def split_into_clauses(text):

    matches = list(
        CLAUSE_PATTERN.finditer(text)
    )

    if not matches:
        return []

    clauses = []

    for index, match in enumerate(matches):

        clause_number = match.group(1)

        start = match.start()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(text)

        clause_text = text[start:end].strip()

        clauses.append({
            "clause": clause_number,
            "text": clause_text
        })

    return clauses

def build_chunk_text(article, clause_text=None):

    header = (
        f"Article {article['article_number']} — "
        f"{article['article_title']}\n"
        f"{article['part']} — "
        f"{article['part_title']}"
    )

    if clause_text:
        return f"{header}\n\n{clause_text}".strip()

    return (
        f"{header}\n\n"
        f"{article['article_text']}"
    ).strip()


def chunk_article(article):

    article_number = article["article_number"]

    body = remove_article_heading(
        article["article_text"],
        article_number
    )


    clauses = split_into_clauses(
        body
    )

    chunks = []

    # No numbered clauses:
    # keep the whole article together.
    if not clauses:

        chunks.append({
            "chunk_id": f"article_{article_number}",
            "article_number": article_number,
            "article_title": article["article_title"],
            "part": article["part"],
            "part_title": article["part_title"],
            "status": article["status"],
            "clause": None,
            "text": build_chunk_text(article),
            "source": article["source"],
            "version": article["version"]
        })

        return chunks

    # Article contains numbered clauses.
    # Article contains numbered clauses.

    clause_counts = {}

    for clause in clauses:

        clause_number = clause["clause"]

        # Track repeated clause numbers within
        # the same article.
        clause_counts[clause_number] = (
            clause_counts.get(clause_number, 0) + 1
        )

        occurrence = clause_counts[clause_number]

        # First occurrence keeps the normal ID.
        if occurrence == 1:

            chunk_id = (
                f"article_{article_number}"
                f"_clause_{clause_number}"
            )

        # Repeated occurrences get a unique suffix.
        else:

            chunk_id = (
                f"article_{article_number}"
                f"_clause_{clause_number}"
                f"_part_{occurrence}"
            )

        chunks.append({
            "chunk_id": chunk_id,
            "article_number": article_number,
            "article_title": article["article_title"],
            "part": article["part"],
            "part_title": article["part_title"],
            "status": article["status"],
            "clause": clause_number,
            "text": build_chunk_text(
                article,
                clause["text"]
            ),
            "source": article["source"],
            "version": article["version"]
        })

    return chunks


def main():

    print("Loading clean Constitution dataset...")

    dataset = load_json(INPUT_PATH)

    articles = dataset["articles"]

    all_chunks = []

    for article in articles:

        article_chunks = chunk_article(article)

        all_chunks.extend(article_chunks)
    # ========================================================
    # VALIDATE UNIQUE CHUNK IDS
    # ========================================================

    chunk_ids = [
        chunk["chunk_id"]
        for chunk in all_chunks
    ]

    duplicate_ids = {
        chunk_id
        for chunk_id in chunk_ids
        if chunk_ids.count(chunk_id) > 1
    }

    print(
        f"Unique chunk IDs: {len(set(chunk_ids))}"
    )

    print(
        f"Duplicate chunk IDs: {len(duplicate_ids)}"
    )

    if duplicate_ids:

        print(
            "Duplicates found:"
        )

        print(
            list(duplicate_ids)[:20]
        )
    output = {
        "source": dataset["source"],
        "version": dataset["version"],
        "language": dataset["language"],
        "total_articles": len(articles),
        "total_chunks": len(all_chunks),
        "chunks": all_chunks
    }

    save_json(
        output,
        OUTPUT_PATH
    )

    print("=" * 60)
    print("CHUNKING COMPLETE")
    print("=" * 60)

    print(f"Articles processed: {len(articles)}")
    print(f"Chunks created: {len(all_chunks)}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()