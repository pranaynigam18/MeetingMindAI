from fastapi import FastAPI, UploadFile, File
from services.transcriber import transcribe_audio
import shutil

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "MeetingMind AI Running"
    }


@app.post("/upload")
def upload_audio(file: UploadFile = File(...)):

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": file.filename,
        "saved_to": file_path
    }


@app.post("/transcribe")
def transcribe(file_name: str):

    file_path = f"uploads/{file_name}"

    transcript = transcribe_audio(file_path)

    return {
        "transcript": transcript
    }

@app.get("/test")
def test():
    return {"status": "working"}