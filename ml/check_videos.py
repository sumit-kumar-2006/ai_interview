import cv2
import glob
import os

files = glob.glob("ml/datasets/raw/train/*.mp4")

print("Files:", len(files))

good = 0
bad = 0

for file in files:
    cap = cv2.VideoCapture(file)

    if not cap.isOpened():
        print("BAD:", os.path.basename(file))
        bad += 1
        continue

    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps > 0:
        duration = frames / fps
    else:
        duration = 0

    print(
        "OK:",
        os.path.basename(file),
        "| Frames:", frames,
        "| FPS:", round(fps, 2),
        "| Duration:", round(duration, 2), "sec"
    )

    cap.release()
    good += 1

print()
print("Valid:", good)
print("Invalid:", bad)