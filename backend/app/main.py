from fastapi import FastAPI
from pydantic import BaseModel, Field

from scripts.query_chroma import search_constitution, build_context
from scripts.gemini_client import generate_answer


app = FastAPI(

    title="Samvidhan AI API",

    description="Indian Constitution Research Assistant",

    version="1.0.0"

)


# ============================================================
# REQUEST MODEL
# ============================================================

class QuestionRequest(BaseModel):

    question: str = Field(
        ...,
        min_length = 1,
        description = "Question about the Constitution of India"
    )


# ============================================================
# ROOT
# ============================================================

@app.get("/")

def root():

    return {

        "message": "Samvidhan AI API is running"

    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")

def health():

    return {

        "status": "healthy"

    }


# ============================================================
# ASK QUESTION
# ============================================================

# ============================================================
# ASK QUESTION
# ============================================================

@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question

    print(
        f"\nReceived question: {question}"
    )

    # --------------------------------------------------------
    # RETRIEVE CONSTITUTIONAL CONTEXT
    # --------------------------------------------------------

    print(
        "\nRetrieving constitutional context..."
    )

    results = search_constitution(
        query=question,
        top_k=8
    )

    context = build_context(
        results
    )

    # --------------------------------------------------------
    # GENERATE ANSWER
    # --------------------------------------------------------

    print(
        "\nGenerating answer with Gemini..."
    )

    answer = generate_answer(
        question,
        context
    )

    # --------------------------------------------------------
    # EXTRACT SOURCE INFORMATION
    # --------------------------------------------------------

    metadatas = results["metadatas"][0]

    sources = []

    seen_articles = set()

    for metadata in metadatas:

        article_number = metadata["article_number"]

        if article_number in seen_articles:
            continue

        seen_articles.add(article_number)

        sources.append({
            "article": article_number,
            "title": metadata["article_title"],
            "part": metadata["part"],
            "part_title": metadata.get("part_title"),
        })

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }