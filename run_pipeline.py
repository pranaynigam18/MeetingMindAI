from services.transcriber import transcribe_audio
from services.intelligence_engine import analyze_meeting
from services.storage import save_meeting
import sys

if len(sys.argv) < 2:
    print("Usage: python run_pipeline.py <audio_file>")
    sys.exit(1)

audio_path = sys.argv[1]

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