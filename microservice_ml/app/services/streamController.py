import cv2
import subprocess
import numpy as np
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn

app = FastAPI()

STREAM_URL = "https://4135ebff68ce.ngrok-free.app:/video"

def generate_frames():
    command = [
        "ffmpeg",
        "-i", STREAM_URL,
        "-f", "image2pipe",
        "-pix_fmt", "bgr24",
        "-vcodec", "rawvideo", "-"
    ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    w, h = 640, 480  # bisa diubah sesuai stream
    frame_size = w * h * 3

    while True:
        raw_frame = process.stdout.read(frame_size)
        if not raw_frame:
            break
        frame = np.frombuffer(raw_frame, np.uint8).reshape((h, w, 3))
        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
