from services.db import conn
from services.gemini_service import model

question = input("Ask MeetingMind: ")

cursor = conn.cursor()

cursor.execute("""
    SELECT meeting_id,
           summary,
           actions,
           decisions,
           risks
    FROM meetings
""")

rows = cursor.fetchall()

all_data = ""

for row in rows:

    all_data += f"""

Meeting ID: {row[0]}

Summary:
{row[1]}

Actions:
{row[2]}

Decisions:
{row[3]}

Risks:
{row[4]}

"""

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