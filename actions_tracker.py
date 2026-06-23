from services.db import conn

cursor = conn.cursor()

cursor.execute("""
    SELECT meeting_id, actions
    FROM meetings
""")

rows = cursor.fetchall()

print("\n===== PENDING ACTIONS =====\n")

for meeting_id, actions in rows:

    for action in actions:

        print(f"Meeting: {meeting_id}")
        print(f"Owner: {action['owner']}")
        print(f"Task: {action['task']}")
        print(f"Deadline: {action['deadline']}")
        print("-" * 40)