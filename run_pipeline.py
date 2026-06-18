from services.transcriber import transcribe_audio
from services.gemini_service import generate_summary
from services.action_extractor import extract_actions

audio_path = "uploads/meeting_test.mp3.ogg"

print("\n===== TRANSCRIBING =====\n")

transcript = transcribe_audio(audio_path)

print(transcript)

print("\n===== SUMMARY =====\n")

summary = generate_summary(transcript)

print(summary)

print("\n===== ACTION ITEMS =====\n")

actions = extract_actions(transcript)

print(actions)