from query_chroma import search_constitution, build_context
from gemini_client import generate_answer


# ============================================================
# TEST QUESTION
# ============================================================

question = "What does Article 368 say?"


# ============================================================
# RETRIEVE CONSTITUTIONAL CONTEXT
# ============================================================

print("\nRetrieving constitutional context...")

results = search_constitution(
    query=question,
    top_k=5
)

context = build_context(
    results
)


# ============================================================
# GENERATE ANSWER USING GEMINI
# ============================================================

print("\nGenerating answer with Gemini...")

answer = generate_answer(
    question,
    context
)


# ============================================================
# DISPLAY FINAL ANSWER
# ============================================================

print("\n" + "=" * 70)
print("SAMVIDHAAN AI ANSWER")
print("=" * 70)

print(answer)