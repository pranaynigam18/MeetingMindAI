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
def meetings(request: Request):

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            meeting_id,
            summary
        FROM meetings
        ORDER BY created_at DESC
    """)

    meetings = cursor.fetchall()

    return templates.TemplateResponse(
        request=request,
        name="meetings.html",
        context={
            "meetings": meetings
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

    actions = meeting[2]
    decisions = meeting[3]
    risks = meeting[4]

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