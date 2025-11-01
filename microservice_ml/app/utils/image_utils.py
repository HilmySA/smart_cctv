import base64
import numpy as np
import cv2

def decode_image(image_base64: str):
    if "," in image_base64:
        image_base64 = image_base64.split(",")[1]
    img_data = base64.b64decode(image_base64)
    np_arr = np.frombuffer(img_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return frame