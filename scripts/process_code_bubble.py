import cv2
import numpy as np
import os
from PIL import Image

src_path = r"C:\Users\Sumit\.gemini\antigravity\brain\a33955dc-d215-48f8-9857-2271a4561998\ai_interview_speech_bubble_1794322760684.jpg"
out_dir = r"d:\AI-Interview-Analyzer\frontend\assets\illustrations"
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "interview_3d_code_speech_bubble_transparent.png")

img = cv2.imread(src_path)
h, w = img.shape[:2]

# Alpha calculation using luminance / color distance from pure white
# Calculate distance from white (255, 255, 255)
b, g, r = cv2.split(img.astype(np.float32))
dist = np.sqrt((255.0 - r)**2 + (255.0 - g)**2 + (255.0 - b)**2)

# Normalize distance: threshold below 8 is transparent, above 35 is fully opaque
alpha = np.clip((dist - 8.0) / 28.0 * 255.0, 0, 255).astype(np.uint8)

# Feather alpha slightly with Gaussian blur
alpha_feathered = cv2.GaussianBlur(alpha, (3, 3), 0)

# Merge BGR and Alpha
b_u8, g_u8, r_u8 = cv2.split(img)
rgba = cv2.merge([b_u8, g_u8, r_u8, alpha_feathered])

pil_img = Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA))
bbox = pil_img.getbbox()
if bbox:
    pad = 14
    crop_box = (max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(w, bbox[2] + pad), min(h, bbox[3] + pad))
    pil_img = pil_img.crop(crop_box)

pil_img.save(out_path, format="PNG")
print(f"SUCCESS: Saved {out_path} ({os.path.getsize(out_path)} bytes, size {pil_img.size})")
