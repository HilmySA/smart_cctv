# app/services/anpr.py
import logging
import cv2
import re
import base64
import traceback
import numpy as np
import easyocr
from PIL import Image

logger = logging.getLogger(__name__)

# ============================================================
# Pattern plat Indonesia
# ============================================================
PLAT_REGEX = re.compile(r"^[A-Z]{1,2}[0-9]{1,4}[A-Z]{0,3}$")

def is_valid_plate(text: str) -> bool:
    return bool(PLAT_REGEX.match(text))

def format_plate(text: str) -> str:
    
    t = text.upper()
    m = re.match(r"^([A-Z]{1,2})([0-9]{1,4})([A-Z]{0,3})$", t)
    if not m:
        return t
    part1, nums, part3 = m.groups()
    if part3:
        return f"{part1} {nums} {part3}"
    return f"{part1} {nums}"

# ============================================================
# Anti false positive
# ============================================================
CHAR_MAP = {
    '0': 'O',
    '1': 'I',
    '5': 'S',
    '8': 'B',
    '6': 'G'
}

def clean_text(txt: str) -> str:
    txt = ''.join(c for c in txt.upper() if c.isalnum())
    return ''.join(CHAR_MAP.get(c, c) for c in txt)

# ============================================================
# Crop to base64
# ============================================================
def crop_to_b64(img):
    if img is None or img.size == 0:
        return ""
    ok, buf = cv2.imencode(".jpg", img)
    if not ok:
        return ""
    return "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode()

# ============================================================
# Warna plat
# ============================================================
def detect_color(crop):
    try:
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        h_mean = hsv[:, :, 0].mean()
        s_mean = hsv[:, :, 1].mean()
        v_mean = hsv[:, :, 2].mean()

        if s_mean > 40 and 10 < h_mean < 45:
            return "yellow"
        if v_mean < 70:
            return "black"
        return "white"
    except:
        return "unknown"


# ============================================================
# ANPR (EasyOCR version)
# ============================================================
class ANPRRecognizer:
    def __init__(self):
        try:
            self.reader = easyocr.Reader(['en'], gpu=False)
            logger.info("EasyOCR ANPR loaded.")
        except Exception as e:
            logger.error(f"Gagal load EasyOCR: {e}")
            self.reader = None

        self.conf_threshold = 0.40

    def recognize_plate(self, frame):
        if self.reader is None:
            return "Error: OCR not initialized"

        try:
            results = self.reader.readtext(frame)
            formatted_results = []

            if not results:
                return "No plate detected"

            for item in results:
                if len(item) != 3:
                    continue

                bbox, text, prob = item

                if prob is None or prob < self.conf_threshold:
                    continue

                if not text or len(text.strip()) == 0:
                    continue

                clean_txt = clean_text(text)

                # Filter plat
                if not is_valid_plate(clean_txt):
                    continue

                # Ambil bbox
                pts = np.array(bbox).astype(int)
                xs = pts[:, 0]
                ys = pts[:, 1]

                left, right = xs.min(), xs.max()
                top, bottom = ys.min(), ys.max()

                # Validasi area
                if top < 0 or left < 0 or bottom <= top or right <= left:
                    continue

                formatted_results.append({
                    "label": f"{clean_txt} ({prob:.2f})",
                    "top": int(top),
                    "left": int(left),
                    "bottom": int(bottom),
                    "right": int(right)
                })

            return formatted_results if formatted_results else "No plate detected"

        except Exception as e:
            logger.error(f"ANPR Fatal Error: {e}")
            logger.error(traceback.format_exc())
            return "Error"


# ============================================================
# Instance global
# ============================================================
anpr_recognizer = ANPRRecognizer()
