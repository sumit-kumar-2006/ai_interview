import subprocess
import glob
import os

VIDEO_DIR = "ml/datasets/raw/train"
AUDIO_DIR = "ml/datasets/audio"

os.makedirs(AUDIO_DIR, exist_ok=True)

videos = glob.glob(os.path.join(VIDEO_DIR, "*.mp4"))

print(f"Found {len(videos)} video files")

success = 0
failed = 0

for video in videos:
    filename = os.path.splitext(os.path.basename(video))[0]
    output = os.path.join(AUDIO_DIR, filename + ".wav")

    print(f"\nExtracting: {os.path.basename(video)}")

    command = [
        "ffmpeg",
        "-y",
        "-i", video,
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-sample_fmt", "s16",
        output
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode == 0:
        print(f"OK: {os.path.basename(output)}")
        success += 1
    else:
        print(f"FAILED: {os.path.basename(video)}")
        print(result.stderr[-500:])
        failed += 1

print("\n==============================")
print("Audio extraction completed")
print("Successful:", success)
print("Failed:", failed)
print("==============================")