from fastapi import FastAPI
from pydantic import BaseModel

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

    question: str


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
        top_k=5
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
    # RESPONSE
    # --------------------------------------------------------

    return {

        "question": question,

        "answer": answer

    }