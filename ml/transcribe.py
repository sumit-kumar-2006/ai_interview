from faster_whisper import WhisperModel
import glob
import os

AUDIO_DIR = "ml/datasets/audio"
OUTPUT_DIR = "ml/datasets/transcripts"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading Whisper model...")

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

audio_files = glob.glob(os.path.join(AUDIO_DIR, "*.wav"))

print(f"Found {len(audio_files)} audio files")

success = 0
failed = 0

for audio_file in audio_files:

    filename = os.path.splitext(os.path.basename(audio_file))[0]
    output_file = os.path.join(OUTPUT_DIR, filename + ".txt")

    print(f"\nTranscribing: {os.path.basename(audio_file)}")

    try:
        segments, info = model.transcribe(
            audio_file,
            beam_size=5
        )

        text = " ".join(segment.text.strip() for segment in segments)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)

        print("OK")
        print("Text:", text[:200])

        success += 1

    except Exception as e:
        print("FAILED:", e)
        failed += 1

print("\n==============================")
print("Transcription completed")
print("Successful:", success)
print("Failed:", failed)
print("==============================")