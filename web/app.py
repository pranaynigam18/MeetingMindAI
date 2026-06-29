from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from services.db import conn
from services.gemini_service import model
from services.transcriber import transcribe_audio
from services.intelligence_engine import analyze_meeting
from services.storage import save_meeting
import json
import shutil
import os
from datetime import datetime

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="web/static"),
    name="static"
)

templates = Jinja2Templates(
    directory="web/templates"
)


@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "answer": None,
            "question": ""
        }
    )


@app.post("/ask")
def ask(request: Request, question: str = Form(...)):

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            meeting_id,
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

Answer the question using ONLY the meeting knowledge provided.

Question:

{question}

Meeting Data:

{all_data}
"""

    try:

        response = model.generate_content(prompt)

        answer = response.text

    except Exception as e:

        answer = f"Error: {str(e)}"

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "question": question,
            "answer": answer
        }
    )


@app.get("/meetings")
def meetings(
    request: Request,
    search: str = ""
):

    cursor = conn.cursor()

    if search:

        cursor.execute(
            """
            SELECT
                meeting_id,
                title,
                summary
            FROM meetings
            WHERE
                title ILIKE %s
                OR summary ILIKE %s
            ORDER BY created_at DESC
            """,
            (
                f"%{search}%",
                f"%{search}%"
            )
        )

    else:

        cursor.execute(
            """
            SELECT
                meeting_id,
                title,
                summary
            FROM meetings
            ORDER BY created_at DESC
            """
        )

    meetings = cursor.fetchall()

    return templates.TemplateResponse(
        request=request,
        name="meetings.html",
        context={
            "meetings": meetings,
            "search": search
        }
    )

@app.get("/meeting/{meeting_id}")
def meeting_detail(
    request: Request,
    meeting_id: str
):

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            meeting_id,
            title,
            summary,
            actions,
            decisions,
            risks
        FROM meetings
        WHERE meeting_id = %s
        """,
        (meeting_id,)
    )

    meeting = cursor.fetchone()

    actions = meeting[3]
    decisions = meeting[4]
    risks = meeting[5]

    return templates.TemplateResponse(
        request=request,
        name="meeting_detail.html",
        context={
            "meeting": meeting,
            "actions": actions,
            "decisions": decisions,
            "risks": risks
        }
    )

@app.get("/upload")
def upload_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="upload.html"
    )


@app.post("/upload")
def upload_audio(
    request: Request,
    audio: UploadFile = File(...)
):

    os.makedirs("uploads", exist_ok=True)

    filepath = f"uploads/{audio.filename}"

    with open(filepath, "wb") as buffer:

        shutil.copyfileobj(
            audio.file,
            buffer
        )

    try:

        transcript = transcribe_audio(filepath)

        result = analyze_meeting(transcript)

        meeting_id = save_meeting(
            transcript,
            result
        )

        return RedirectResponse(
            url=f"/meeting/{meeting_id}",
            status_code=303
        )

    except Exception as e:

        return templates.TemplateResponse(
            request=request,
            name="upload.html",
            context={
                "message": f"Error: {str(e)}"
            }
        )
    
@app.get("/dashboard")
def dashboard(request: Request):

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM meetings
    """)

    total_meetings = cursor.fetchone()[0]

    cursor.execute("""
        SELECT
            actions,
            decisions,
            risks
        FROM meetings
    """)

    rows = cursor.fetchall()

    total_actions = 0
    total_decisions = 0
    total_risks = 0

    for row in rows:

        total_actions += len(row[0])
        total_decisions += len(row[1])
        total_risks += len(row[2])

    # Pending Actions

    cursor.execute("""
        SELECT
            meeting_id,
            actions
        FROM meetings
    """)

    action_rows = cursor.fetchall()

    pending_actions = []

    print("\n===== ACTION ROWS =====")
    print(action_rows)
    print("=======================\n")

    for meeting_id, actions in action_rows:

        for action in actions:

            pending_actions.append(action)

    # Recent Risks
    owner_stats = {}
    for action in pending_actions:
        owner = action.get("owner", "Unknown")
        
        if owner not in owner_stats:
            owner_stats[owner] = 0
        owner_stats[owner] += 1

        print("\n===== OWNER STATS =====")
        print(owner_stats)
        print("=======================\n")
        
    cursor.execute("""
        SELECT
            meeting_id,
            risks
        FROM meetings
    """)

    risk_rows = cursor.fetchall()

    recent_risks = []

    for meeting_id, risks in risk_rows:

        for risk in risks:

            recent_risks.append(risk)

    # Recent Meetings

    cursor.execute("""
    SELECT
        meeting_id,
        title,
        summary
    FROM meetings
    ORDER BY created_at DESC
    LIMIT 5
""")

    recent_meetings = cursor.fetchall()


    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "total_meetings": total_meetings,
            "total_actions": total_actions,
            "total_decisions": total_decisions,
            "total_risks": total_risks,
            "pending_actions": pending_actions,
            "recent_risks": recent_risks,
            "recent_meetings": recent_meetings,
            "owner_stats": owner_stats,
        }
    )

@app.get("/decisions")
def decisions(request: Request):

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            meeting_id,
            title,
            decisions
        FROM meetings
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()

    all_decisions = []

    for meeting_id, title, decisions in rows:

        for decision in decisions:

            all_decisions.append({
                "meeting_id": meeting_id,
                "title": title,
                "decision": decision["decision"]
            })

    return templates.TemplateResponse(
        request=request,
        name="decisions.html",
        context={
            "decisions": all_decisions
        }
    )


@app.get("/decision-timeline")
def decision_timeline(request: Request):

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            meeting_id,
            title,
            decisions,
            created_at
        FROM meetings
        ORDER BY created_at ASC
    """)

    rows = cursor.fetchall()

    decision_map = {}

    for meeting_id, title, decisions, created_at in rows:

        for decision in decisions:

            decision_text = decision["decision"].strip()

            decision_key = decision_text.lower()

            if decision_key not in decision_map:

                decision_map[decision_key] = {
                    "decision": decision_text,
                    "first_meeting_id": meeting_id,
                    "first_meeting_title": title,
                    "first_mention": created_at,
                    "last_mention": created_at,
                    "mention_count": 0,
                    "related_meetings": []
                }

            decision_map[decision_key]["mention_count"] += 1
            decision_map[decision_key]["related_meetings"].append(meeting_id)

            if created_at > decision_map[decision_key]["last_mention"]:
                decision_map[decision_key]["last_mention"] = created_at

    merged_decisions = list(decision_map.values())

    merged_decisions.sort(
        key=lambda x: x["last_mention"],
        reverse=True
    )

    return templates.TemplateResponse(
        request=request,
        name="decision_timeline.html",
        context={
            "decisions": merged_decisions
        }
    )


@app.get("/executive")
def executive(request: Request):

    cursor = conn.cursor()

    # Meetings This Month
    current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    cursor.execute("""
        SELECT COUNT(*)
        FROM meetings
        WHERE created_at >= %s
    """, (current_month,))

    meetings_this_month = cursor.fetchone()[0]

    # Total Decisions
    cursor.execute("""
        SELECT decisions
        FROM meetings
    """)

    rows = cursor.fetchall()

    total_decisions = 0

    for row in rows:
        total_decisions += len(row[0])

    # Pending Actions
    cursor.execute("""
        SELECT actions
        FROM meetings
    """)

    rows = cursor.fetchall()

    pending_actions = 0

    for row in rows:
        pending_actions += len(row[0])

    # High Risks
    cursor.execute("""
        SELECT risks
        FROM meetings
    """)

    rows = cursor.fetchall()

    high_risks = 0

    for row in rows:
        for risk in row[0]:
            if risk.get("severity", "").lower() == "high":
                high_risks += 1

    # Top Action Owner
    cursor.execute("""
        SELECT actions
        FROM meetings
    """)

    rows = cursor.fetchall()

    owner_stats = {}

    for row in rows:
        for action in row[0]:
            owner = action.get("owner", "Unknown")
            if owner not in owner_stats:
                owner_stats[owner] = 0
            owner_stats[owner] += 1

    top_action_owner = None
    top_action_count = 0

    if owner_stats:
        top_action_owner = max(owner_stats, key=owner_stats.get)
        top_action_count = owner_stats[top_action_owner]

    # Latest Decision
    cursor.execute("""
        SELECT meeting_id, title, decisions, created_at
        FROM meetings
        WHERE decisions != '[]'::jsonb
        ORDER BY created_at DESC
        LIMIT 1
    """)

    latest_decision_row = cursor.fetchone()

    latest_decision = None

    if latest_decision_row:
        latest_decision = {
            "meeting_id": latest_decision_row[0],
            "title": latest_decision_row[1],
            "decision": latest_decision_row[2][0]["decision"] if latest_decision_row[2] else None,
            "created_at": latest_decision_row[3]
        }

    # Latest Risk
    cursor.execute("""
        SELECT meeting_id, title, risks, created_at
        FROM meetings
        WHERE risks != '[]'::jsonb
        ORDER BY created_at DESC
        LIMIT 1
    """)

    latest_risk_row = cursor.fetchone()

    latest_risk = None

    if latest_risk_row:
        latest_risk = {
            "meeting_id": latest_risk_row[0],
            "title": latest_risk_row[1],
            "risk": latest_risk_row[2][0]["risk"] if latest_risk_row[2] else None,
            "severity": latest_risk_row[2][0]["severity"] if latest_risk_row[2] else None,
            "created_at": latest_risk_row[3]
        }

    # Latest Meeting
    cursor.execute("""
        SELECT meeting_id, title, summary, created_at
        FROM meetings
        ORDER BY created_at DESC
        LIMIT 1
    """)

    latest_meeting_row = cursor.fetchone()

    latest_meeting = None

    if latest_meeting_row:
        latest_meeting = {
            "meeting_id": latest_meeting_row[0],
            "title": latest_meeting_row[1],
            "summary": latest_meeting_row[2],
            "created_at": latest_meeting_row[3]
        }

    return templates.TemplateResponse(
        request=request,
        name="executive.html",
        context={
            "meetings_this_month": meetings_this_month,
            "total_decisions": total_decisions,
            "pending_actions": pending_actions,
            "high_risks": high_risks,
            "top_action_owner": top_action_owner,
            "top_action_count": top_action_count,
            "latest_decision": latest_decision,
            "latest_risk": latest_risk,
            "latest_meeting": latest_meeting
        }
    )


@app.get("/discussions")
def discussions(request: Request):

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            meeting_id,
            title,
            topics,
            created_at
        FROM meetings
        ORDER BY created_at ASC
    """)

    rows = cursor.fetchall()

    topic_map = {}

    for meeting_id, title, topics, created_at in rows:

        if not topics:
            continue

        for topic in topics:

            if isinstance(topic, dict):
                topic_text = topic.get("topic", "").strip()
            else:
                topic_text = topic.strip()

            topic_key = topic_text.lower()

            if topic_key not in topic_map:

                topic_map[topic_key] = {
                    "topic": topic_text,
                    "first_meeting_id": meeting_id,
                    "first_meeting_title": title,
                    "first_mention": created_at,
                    "last_mention": created_at,
                    "mention_count": 0,
                    "related_meetings": []
                }

            topic_map[topic_key]["mention_count"] += 1
            topic_map[topic_key]["related_meetings"].append(meeting_id)

            if created_at > topic_map[topic_key]["last_mention"]:
                topic_map[topic_key]["last_mention"] = created_at

    merged_topics = list(topic_map.values())

    merged_topics.sort(
        key=lambda x: x["last_mention"],
        reverse=True
    )

    return templates.TemplateResponse(
        request=request,
        name="discussions.html",
        context={
            "topics": merged_topics
        }
    )