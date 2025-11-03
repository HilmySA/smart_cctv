import cv2
import threading
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from fastapi.responses import StreamingResponse
import uvicorn

RTSP_URL = "rtsp://10.15.221.182:8080/h264.sdp"

app = FastAPI()

# ----- HTML sederhana -----
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>RTSP MJPEG Stream</title>
</head>
<body>
    <h1>RTSP MJPEG Stream via HTTP</h1>
    <img src="/mjpeg" width="640" height="480"/>
</body>
</html>
"""

@app.get("/")
async def index():
    return HTMLResponse(html_content)


# ----- RTSP Reader dengan thread -----
class RTSPReader:
    def __init__(self, url):
        self.url = url
        self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.ret = False
        self.frame = None
        self.stopped = False
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            if not ret:
                print("Gagal ambil frame, reconnect...")
                self.cap.release()
                self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                continue
            with self.lock:
                self.ret = ret
                self.frame = frame

    def read(self):
        with self.lock:
            return self.ret, self.frame.copy() if self.frame is not None else None

    def stop(self):
        self.stopped = True
        self.thread.join()
        self.cap.release()


reader = RTSPReader(RTSP_URL)


# ----- MJPEG streaming endpoint -----
@app.get("/mjpeg")
def mjpeg_stream():
    def generate():
        while True:
            ret, frame = reader.read()
            if not ret:
                continue
            # Encode ke JPEG
            _, buffer = cv2.imencode(".jpg", frame)
            frame_bytes = buffer.tobytes()
            # Multipart MJPEG
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
    
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")


# ----- Run FastAPI langsung -----
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
