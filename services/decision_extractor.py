from services.gemini_service import model
import json

def extract_decisions(transcript):

    prompt = f"""
You are an expert meeting assistant.

Extract all decisions made during the meeting.

Return ONLY valid JSON.

Example:

[
  {{
    "decision":"Use PostgreSQL instead of MongoDB"
  }}
]

If no decisions exist return:

[]

Transcript:

{transcript}
"""

    response = model.generate_content(prompt)

    clean_text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean_text)