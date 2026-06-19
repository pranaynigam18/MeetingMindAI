from services.gemini_service import model
import json

def detect_risks(transcript):

    prompt = f"""
You are an expert project risk analyst.

Analyze the meeting transcript carefully.

Identify all risks, blockers, delays, dependencies, missing approvals,
resource issues, timeline risks, or anything that could negatively impact
the project.

Return ONLY valid JSON.

Format:

[
  {{
    "risk":"",
    "severity":"low|medium|high"
  }}
]

If no risks exist return:

[]

Transcript:

{transcript}
"""

    response = model.generate_content(prompt)

    clean_text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean_text)