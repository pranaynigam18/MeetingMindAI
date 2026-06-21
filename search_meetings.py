from services.db import conn

query = input("Enter keyword: ").lower()

cursor = conn.cursor()

cursor.execute(
    """
    SELECT meeting_id, summary
    FROM meetings
    WHERE LOWER(transcript) LIKE %s
    """,
    (f"%{query}%",)
)

results = cursor.fetchall()

print("\nSearching...\n")

for meeting_id, summary in results:

    print("=" * 50)
    print("Meeting:", meeting_id)

    print("\nSummary:")
    print(summary[:300])