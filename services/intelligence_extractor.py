from services.gemini_service import model
import json


def extract_intelligence(transcript):

    prompt = f"""
You are MeetingMind AI.

Analyze the meeting transcript.

Return ONLY valid JSON.

Required format:

{{
  "summary": "string",

  "people": [
    {{
      "name": "string"
    }}
  ],

  "topics": [
    {{
      "topic": "string"
    }}
  ],

  "actions": [
    {{
      "owner": "string",
      "task": "string",
      "deadline": "string"
    }}
  ],

  "decisions": [
    {{
      "decision": "string"
    }}
  ],

  "risks": [
    {{
      "risk": "string",
      "severity": "high|medium|low"
    }}
  ]
}}

Return ONLY JSON.

Transcript:

{transcript}
"""

    response = model.generate_content(prompt)

    clean_text = (
        response.text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:
        return json.loads(clean_text)
    
    except Exception as e:
        print("JSON Parse Error:", e)
        
        return {
        "summary": "",
        "people": [],
        "topics": [],
        "actions": [],
        "decisions": [],
        "risks": []
    }