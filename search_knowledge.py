import json
import os

query = input("Ask about: ").lower()

folder = "data/meetings"

found = False

for file in os.listdir(folder):

    if not file.endswith(".json"):
        continue

    path = os.path.join(folder, file)

    with open(path, "r", encoding="utf-8") as f:
        meeting = json.load(f)

    # Search Decisions
    for decision in meeting.get("decisions", []):

        if query in decision["decision"].lower():

            found = True

            print("\n" + "=" * 60)
            print("Meeting:", meeting["meeting_id"])

            print("\nDecision:")
            print(decision["decision"])

            print("\nSummary:")
            print(meeting["summary"][:400])

if not found:
    print("\nNo matching knowledge found.")