import json
import os

query = input("Enter keyword: ").lower()

folder = "data/meetings"

print("\nSearching...\n")

for file in os.listdir(folder):

    if not file.endswith(".json"):
        continue

    path = os.path.join(folder, file)

    with open(path, "r", encoding="utf-8") as f:
        meeting = json.load(f)

    transcript = meeting.get("transcript", "").lower()

    if query in transcript:

        print("=" * 50)
        print("Meeting:", file)

        print("\nSummary:")
        print(meeting["summary"][:300])

        print("\nDecisions:")

        for d in meeting.get("decisions", []):
            print("-", d["decision"])