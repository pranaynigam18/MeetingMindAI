import json
import os
from datetime import datetime

from services.db import conn


def save_meeting(transcript, result):

    os.makedirs("data/meetings", exist_ok=True)

    meeting_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    meeting_data = {
        "meeting_id": meeting_id,
        "people": result["people"],
        "topics": result["topics"],
        "created_at": datetime.now().isoformat(),
        "transcript": transcript,
        "summary": result["summary"],
        "actions": result["actions"],
        "decisions": result["decisions"],
        "risks": result["risks"]
    }

    filepath = f"data/meetings/meeting_{meeting_id}.json"

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(
            meeting_data,
            f,
            indent=4,
            ensure_ascii=False
        )

    # PostgreSQL Save

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO meetings
        (
            meeting_id,
            created_at,
            summary,
            transcript,
            people,
            topics,
            actions,
            decisions,
            risks
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            meeting_id,
            datetime.now(),
            result["summary"],
            transcript,
            json.dumps(result["people"]),
            json.dumps(result["topics"]),
            json.dumps(result["actions"]),
            json.dumps(result["decisions"]),
            json.dumps(result["risks"])
        )
    )

    conn.commit()

    return filepath