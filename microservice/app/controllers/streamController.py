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
from app.services.anpr import anpr_recognizer

logger = logging.getLogger(__name__)

class StreamController:
    def __init__(self):
        self.RTSP_URL = "rtsp://10.15.221.182:8080/h264.sdp"
        self.reader = RTSPReader(self.RTSP_URL)

        self.last_face_data = []
        self.last_anpr_data = []
        self.last_motion = "-"
        self.last_update = None
        self.frame_width = 640
        self.frame_height = 480
        self.active_websockets = set()
        
        self.loop = None # ✏️ Akan diisi oleh startup event
        self.mqtt_connected = False # ✏️ Penanda status
        self.analysis_counter = 0 # ✅ SOLUSI FREEZE ANDA SUDAH BENAR

        # ✏️ DIUBAH: HANYA buat instance, JANGAN connect
        try:
            self.mqtt = MQTTHelper(client_id_prefix="ml-backend")
            logger.info("Instance MQTTHelper dibuat (belum konek).")
        except Exception as e:
            logger.error(f"Gagal membuat instance MQTT: {e}")
            self.mqtt = None

        # Jalankan analisis di thread terpisah
        threading.Thread(target=self.background_analysis, daemon=True).start()

    # ➕ BARU: Method Async untuk Startup Event
    async def connect_mqtt(self):
        if self.mqtt:
            try:
                await self.mqtt.connect() # ❗️ Pakai 'await'
                self.mqtt_connected = True
                logger.info("MQTT terhubung (via startup event).")
            except Exception as e:
                self.mqtt_connected = False
                logger.error(f"Gagal koneksi awal ke MQTT (startup): {e}")

    # ➕ BARU: Method Async untuk Shutdown Event
    async def disconnect_mqtt(self):
        if self.mqtt and self.mqtt_connected:
            try:
                await self.mqtt.disconnect() # ❗️ Pakai 'await'
                self.mqtt_connected = False
                logger.info("MQTT terputus (via shutdown event).")
            except Exception as e:
                logger.error(f"Gagal saat disconnect MQTT: {e}")

    # ... (get_index dan stream_mjpeg tetap sama) ...
    def get_index(self):
        return HTMLResponse(index_html)
    def stream_mjpeg(self):
        def generate():
            while True:
                ret, frame = self.reader.read()
                if not ret: continue
                self.frame_height, self.frame_width = frame.shape[:2]
                _, buffer = cv2.imencode(".jpg", frame)
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")
        return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")


    # ✅ Analisis wajah di background (LOGIKA ANDA SUDAH BENAR)
    def background_analysis(self):
        while True:
            ret, frame = self.reader.read()
            if not ret:
                time.sleep(0.1)
                continue

            try:
                self.frame_height, self.frame_width = frame.shape[:2]
                self.analysis_counter += 1
                
                mqtt_payload = {} 
                
                # ✏️ DIUBAH: Jalankan ANPR hanya 1 dari 10 frame (misal, di frame ke-10)
                if self.analysis_counter % 3 == 0:
                    anpr_results = anpr_recognizer.recognize_plate(frame)
                    if isinstance(anpr_results, list):
                        self.last_anpr_data = anpr_results
                        plate_labels = [p["label"] for p in anpr_results]
                        if plate_labels:
                            mqtt_payload["plate"] = ", ".join(plate_labels)
                    else:
                        self.last_anpr_data = [] 
                
                # ✏️ DIUBAH: Jalankan FR di 9 frame lainnya (prioritas utama)
                else:
                    face_results = recognizer.verify_face(frame)
                    if isinstance(face_results, list):
                        self.last_face_data = face_results
                        label_names = [f["label"] for f in face_results]
                        if label_names:
                             mqtt_payload["face"] = ", ".join(label_names)
                    else:
                        self.last_face_data = [] 
                
                # Reset counter agar tidak terlalu besar (opsional tapi bagus)
                if self.analysis_counter > 1000:
                    self.analysis_counter = 0

                if mqtt_payload:
                    self.send_to_mqtt(mqtt_payload)

                self.last_update = datetime.now(timezone.utc)
                self.push_ws_update() 

            except Exception as e:
                logger.error(f"Error analisis frame: {e}")

            time.sleep(0.1)

    # ✏️ DIUBAH: push_ws_update (Gunakan self.loop)
    def push_ws_update(self):
        if not self.loop: return # Cek jika loop belum siap
            
        data = {
            "faces": self.last_face_data,
            "plates": self.last_anpr_data,
            "motion": self.last_motion,
            "timestamp": self.last_update.isoformat() if self.last_update else None,
            "frame_width": self.frame_width,
            "frame_height": self.frame_height
        }
        message = json.dumps(data)
        dead_clients = []
        for ws in self.active_websockets:
            try:
                # ❗️ Gunakan self.loop yang disimpan
                asyncio.run_coroutine_threadsafe(ws.send_text(message), self.loop)
            except Exception:
                dead_clients.append(ws)
        for ws in dead_clients:
            self.active_websockets.remove(ws)

    # ✏️ DIUBAH: ws_detections (Tidak perlu set loop lagi)
    async def ws_detections(self, websocket: WebSocket):
        await websocket.accept()
        # ❌ HAPUS: websocket.loop = asyncio.get_event_loop()
        self.active_websockets.add(websocket)
        try:
            while True:
                await websocket.receive_text() 
        except Exception:
            self.active_websockets.remove(websocket)

    # ❗️❗️ INI ADALAH FUNGSI YANG DIPERBAIKI (FINAL v2)
    def send_to_mqtt(self, payload):
        """
        Dipanggil dari thread 'background_analysis'.
        Kita menggunakan 'lambda' di dalam 'call_soon_threadsafe'
        untuk memanggil 'publish' dengan keyword argument (qos).
        """
        
        # Cek jika loop, mqtt, atau koneksi belum siap
        if not self.loop or not self.mqtt or not self.mqtt_connected:
            logger.warning("MQTT koneksi belum siap. Publish dilewati.")
            return
        
        try:
            # Siapkan log data
            log_data = {
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            }
            if "face" in payload: log_data["face"] = payload["face"]
            if "plate" in payload: log_data["plate"] = payload["plate"]

            # 1. Panggil publish untuk aktuator (dibungkus lambda)
            self.loop.call_soon_threadsafe(
                lambda: self.mqtt.publish(
                    "aktuator/solenoid",
                    '{"status": true}',
                    qos=1
                )
            )
            
            # 2. Panggil publish untuk log (dibungkus lambda)
            self.loop.call_soon_threadsafe(
                lambda: self.mqtt.publish(
                    "log/deteksi/kamera1",
                    json.dumps(log_data),
                    qos=0
                )
            )
            
        except Exception as e:
            # Tangkap jika ada error saat mendelegasikan panggilan
            logger.error(f"Gagal mendelegasikan panggilan MQTT (lambda): {e}")