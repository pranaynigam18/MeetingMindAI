import json
import os

folder = "data/meetings"

for file in os.listdir(folder):

    if file.endswith(".json"):

        path = os.path.join(folder, file)

        with open(path, "r", encoding="utf-8") as f:
            meeting = json.load(f)

        print("\n" + "=" * 50)
        print(file)

        decisions = meeting.get("decisions", [])

        if isinstance(decisions, str):
            print("Old format file - skipping")
            continue

        for decision in decisions:
            print("- " + decision["decision"])