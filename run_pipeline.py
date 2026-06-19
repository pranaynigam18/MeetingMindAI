from services.transcriber import transcribe_audio
from services.intelligence_engine import analyze_meeting
from services.storage import save_meeting

audio_path = "uploads/meeting_test.mp3.ogg"

print("\n===== TRANSCRIBING =====\n")

transcript = transcribe_audio(audio_path)

print(transcript)

print("\n===== ANALYZING =====\n")

result = analyze_meeting(transcript)
filepath = save_meeting(
    transcript,
    result
)

print("\nSaved To:")
print(filepath)
print(result)