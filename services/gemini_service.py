import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def generate_summary(transcript):
    prompt = f"""
    Summarize this meeting transcript.

    Give:
    1. Summary
    2. Key Points

    Transcript:

    {transcript}
    """

    response = model.generate_content(prompt)

    return response.text
