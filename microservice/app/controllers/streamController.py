import cv2
import threading
import time
import json
import logging
import asyncio
from datetime import datetime, timezone
from fastapi import WebSocket
from fastapi.responses import StreamingResponse, HTMLResponse

# Import service internal
from app.services.rtspReader import RTSPReader
from app.views.templates import index_html
from app.services.faceRecognition import recognizer
from app.services.mqttHelper import MQTTHelper

logger = logging.getLogger(__name__)

class StreamController:
    def __init__(self):
        self.RTSP_URL = "rtsp://10.15.221.182:8080/h264.sdp"
        self.reader = RTSPReader(self.RTSP_URL)

        self.last_face_data = []
        self.last_motion = "-"
        self.last_update = None
        self.frame_width = 640
        self.frame_height = 480
        self.active_websockets = set()

        # ✅ MQTT hanya dibuat sekali
        try:
            self.mqtt = MQTTHelper(client_id_prefix="ml-backend")
            self.mqtt.connect()
            logger.info("MQTT terhubung pada inisialisasi StreamController.")
        except Exception as e:
            logger.error(f"Gagal koneksi awal ke MQTT: {e}")
            self.mqtt = None

        # Jalankan analisis di thread terpisah
        threading.Thread(target=self.background_analysis, daemon=True).start()

    # View utama
    def get_index(self):
        return HTMLResponse(index_html)

    # Stream video MJPEG
    def stream_mjpeg(self):
        def generate():
            while True:
                ret, frame = self.reader.read()
                if not ret:
                    continue

                self.frame_height, self.frame_width = frame.shape[:2]
                _, buffer = cv2.imencode(".jpg", frame)
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")

        return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

    # Analisis wajah di background
    def background_analysis(self):
        while True:
            ret, frame = self.reader.read()
            if not ret:
                time.sleep(0.1)
                continue

            try:
                self.frame_height, self.frame_width = frame.shape[:2]
                face_results = recognizer.verify_face(frame)

                if isinstance(face_results, list):
                    self.last_face_data = face_results
                    label_names = [f["label"] for f in face_results]
                    self.send_to_mqtt({"face": ", ".join(label_names)})
                else:
                    self.last_face_data = []

                self.last_update = datetime.now(timezone.utc)
                self.push_ws_update()

            except Exception as e:
                logger.error(f"Error analisis frame: {e}")

            time.sleep(0.5)

    # Kirim data ke semua client WebSocket aktif
    def push_ws_update(self):
        data = {
            "faces": self.last_face_data,
            "motion": self.last_motion,
            "timestamp": self.last_update.isoformat() if self.last_update else None,
            "frame_width": self.frame_width,
            "frame_height": self.frame_height
        }
        message = json.dumps(data)
        dead_clients = []
        for ws in self.active_websockets:
            try:
                asyncio.run_coroutine_threadsafe(ws.send_text(message), ws.loop)
            except Exception:
                dead_clients.append(ws)
        for ws in dead_clients:
            self.active_websockets.remove(ws)

    # WebSocket endpoint
    async def ws_detections(self, websocket: WebSocket):
        await websocket.accept()
        websocket.loop = asyncio.get_event_loop()
        self.active_websockets.add(websocket)
        try:
            while True:
                await websocket.receive_text()  # dummy read agar koneksi tetap hidup
        except Exception:
            self.active_websockets.remove(websocket)

    # ✅ MQTT sender (gunakan koneksi yang sama)
    def send_to_mqtt(self, result):
        try:
            # Jika MQTT belum terhubung atau putus, coba reconnect
            if self.mqtt is None:
                self.mqtt = MQTTHelper(client_id_prefix="ml-backend")
                self.mqtt.connect()
                logger.info("MQTT reconnect berhasil.")

            self.mqtt.publish(
                "aktuator/solenoid",
                '{"status": true}',
                qos=1
            )
            self.mqtt.publish(
                "log/deteksi/kamera1",
                json.dumps({
                    "face": result.get("face", ""),
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                }),
                qos=0,
            )

        except Exception as e:
            logger.error(f"Gagal kirim data MQTT: {e}")
            # Jika error, tandai agar reconnect di panggilan berikutnya
            self.mqtt = None

    def __del__(self):
        try:
            if self.mqtt:
                self.mqtt.disconnect()
        except Exception:
            pass
