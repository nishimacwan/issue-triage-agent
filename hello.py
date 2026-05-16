from dotenv import load_dotenv
import os

load_dotenv()  # reads .env and makes the keys available

# Import the new Google Gen AI library
from google import genai

# Create a client using our API key
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Ask Gemini a question
response = client.models.generate_content(
    model="gemini-flash-latest",
    contents="In one sentence, what is a GitHub issue?"
)

# Print the answer
print(response.text)