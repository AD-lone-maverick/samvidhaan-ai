import os

from dotenv import load_dotenv
from google import genai


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ============================================================
# GENERATE CONSTITUTIONAL ANSWER
# ============================================================

def generate_answer(
    question,
    context
):

    prompt = f"""
You are Samvidhaan AI, an AI assistant that answers
questions about the Constitution of India.

Answer the user's question using ONLY the constitutional
context provided below.

Do not use outside knowledge.

If the provided context does not contain enough information
to answer the question, clearly say that the available
constitutional context is insufficient.

Give a clear and concise answer.

Do not mention that you are using a language model.

------------------------------------------------------------
USER QUESTION
------------------------------------------------------------

{question}

------------------------------------------------------------
CONSTITUTIONAL CONTEXT
------------------------------------------------------------

{context}

------------------------------------------------------------
ANSWER
------------------------------------------------------------
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    return interaction.output_text