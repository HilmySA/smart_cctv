import cv2
from fastapi.responses import StreamingResponse, HTMLResponse
from app.services.rtspReader import RTSPReader
from app.views.templates import index_html

class StreamController:
    def __init__(self):
        self.RTSP_URL = "rtsp://10.15.221.182:8080/h264.sdp"
        self.reader = RTSPReader(self.RTSP_URL)

    def get_index(self):
        return HTMLResponse(index_html)

    def stream_mjpeg(self):
        def generate():
            while True:
                ret, frame = self.reader.read()
                if not ret:
                    continue
                _, buffer = cv2.imencode(".jpg", frame)
                frame_bytes = buffer.tobytes()
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

        return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")
