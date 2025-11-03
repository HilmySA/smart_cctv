import cv2
import threading
import time
import logging
from datetime import datetime, timezone
from fastapi.responses import StreamingResponse, HTMLResponse
from app.services.rtspReader import RTSPReader
from app.views.templates import index_html
from app.services.faceRecognition import recognizer
# from app.services.motionDetection import detect_movement_by_hip
from app.services.try_mqttHelper import MQTTHelper

logger = logging.getLogger(__name__)

class StreamController:
    def __init__(self):
        self.RTSP_URL = "rtsp://10.15.221.182:8080/h264.sdp"
        self.reader = RTSPReader(self.RTSP_URL)

        # Simpan hasil deteksi terakhir
        self.last_face_data = []
        self.last_motion = "-"
        self.last_update = None

        # Jalankan analisis di background
        threading.Thread(target=self.background_analysis, daemon=True).start()

    # =====================================================
    # ⛩️  View utama (HTML)
    # =====================================================
    def get_index(self):
        return HTMLResponse(index_html)

    # =====================================================
    # 📡  Streaming video MJPEG (tanpa overlay)
    # =====================================================
    def stream_mjpeg(self):
        def generate():
            while True:
                ret, frame = self.reader.read()
                if not ret:
                    continue

                # Encode frame ke JPEG
                _, buffer = cv2.imencode(".jpg", frame)
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")

        return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

    # =====================================================
    # 🧠  Background analisis wajah + gerakan
    # =====================================================
    def background_analysis(self):
        while True:
            ret, frame = self.reader.read()
            if not ret:
                time.sleep(0.1)
                continue

            try:
                face_results = recognizer.verify_face(frame)
                # motion_result = detect_movement_by_hip(frame)

                if isinstance(face_results, list):
                    self.last_face_data = face_results
                    label_names = [f["label"] for f in face_results]
                    self.send_to_mqtt({
                        "face": ", ".join(label_names)
                        # "motion": motion_result
                    })
                else:
                    self.last_face_data = []

                # self.last_motion = motion_result
                self.last_update = datetime.now(timezone.utc)

            except Exception as e:
                logger.error(f"Error analisis frame: {e}")

            time.sleep(2)

    # =====================================================
    # 📦  API untuk kirim data deteksi (JSON)
    # =====================================================
    def get_detection_data(self):
        data = {
            "faces": self.last_face_data,
            # "motion": self.last_motion,
            "timestamp": self.last_update.isoformat() if self.last_update else None
        }
        return data

    # =====================================================
    # ☁️  MQTT sender
    # =====================================================
    def send_to_mqtt(self, result):
        try:
            with MQTTHelper(client_id_prefix="ml-backend") as mqtt:
                mqtt.publish("perintah/aktuator/solenoid", '{"status": true}', qos=1)
                mqtt.publish(
                    "log/deteksi/kamera1",
                    f'{{"face": "{result["face"]}", "motion": "{result["motion"]}", "timestamp": "{datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}"}}',
                    qos=0,
                )
        except Exception as e:
            logger.error(f"Gagal menjalankan skenario MQTT: {e}")
