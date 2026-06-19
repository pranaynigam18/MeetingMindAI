import json
import os

from services.gemini_service import model

question = input("Ask MeetingMind: ")

all_data = ""

folder = "data/meetings"

for file in os.listdir(folder):

    if not file.endswith(".json"):
        continue

    path = os.path.join(folder, file)

    with open(path, "r", encoding="utf-8") as f:

        meeting = json.load(f)

        all_data += json.dumps(
            meeting,
            indent=2
        )

        all_data += "\n\n"


prompt = f"""
You are MeetingMind AI.

Answer the question using only the meeting knowledge provided.

Question:

{question}

Meeting Data:

{all_data}
"""

response = model.generate_content(prompt)

print("\n")
print(response.text)