from services.db import conn
from services.gemini_service import model

question = input("Ask MeetingMind: ")
q = question.lower()

cursor = conn.cursor()

# Intent Detection

if any(word in q for word in [
    "decision",
    "decide",
    "decided",
    "choice",
    "chosen",
    "database"
]):
    data_type = "decisions"

elif any(word in q for word in [
    "risk",
    "risks",
    "problem",
    "problems",
    "issue",
    "issues",
    "blocker",
    "blockers"
]):
    data_type = "risks"

elif any(word in q for word in [
    "action",
    "actions",
    "task",
    "tasks",
    "owner",
    "owns",
    "responsible",
    "assigned"
]):
    data_type = "actions"

else:
    data_type = "all"


# Retrieval

if data_type == "decisions":

    cursor.execute("""
        SELECT meeting_id, decisions
        FROM meetings
    """)

    rows = cursor.fetchall()

    all_data = ""

    for meeting_id, decisions in rows:

        all_data += f"""
Meeting ID: {meeting_id}

Decisions:
{decisions}

"""


elif data_type == "risks":

    cursor.execute("""
        SELECT meeting_id, risks
        FROM meetings
    """)

    rows = cursor.fetchall()

    all_data = ""

    for meeting_id, risks in rows:

        all_data += f"""
Meeting ID: {meeting_id}

Risks:
{risks}

"""


elif data_type == "actions":

    cursor.execute("""
        SELECT meeting_id, actions
        FROM meetings
    """)

    rows = cursor.fetchall()

    all_data = ""

    for meeting_id, actions in rows:

        all_data += f"""
Meeting ID: {meeting_id}

Actions:
{actions}

"""


else:

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