from services.gemini_service import model


def extract_actions(transcript):

    prompt = f"""
You are an expert meeting assistant.
Analyze the transcript carefully.
Pay close attention to names, deadlines, commitments, and assigned responsibilities.
Extract all the action items from the transcript. 


Return ONLY valid JSON.

Example:

[
  {{
    "owner":"Aayush",
    "task":"Complete frontend",
    "deadline":"Friday"
  }}
]

If no action items exist return:

[]

Transcript:

{transcript}
"""

    response = model.generate_content(prompt)

    return response.text