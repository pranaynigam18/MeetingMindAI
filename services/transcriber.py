import whisper

print("Loading Whisper Model...")

model = whisper.load_model("base")

print("Model Loaded Successfully")

def transcribe_audio(file_path):
    result = model.transcribe(file_path)
    return result["text"]