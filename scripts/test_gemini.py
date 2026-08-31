import os
from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input="Say hello to Samvidhaan AI in one sentence."
)


print("\nGemini response:")
print(interaction.output_text)