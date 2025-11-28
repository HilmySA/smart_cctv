import cv2
import threading
import time
import json
import logging
import asyncio
import os # ➕ BARU
from datetime import datetime, timezone, time as dt_time # ➕ BARU
from dotenv import load_dotenv # ➕ BARU
from supabase import create_client, Client # ➕ BARU

from fastapi import WebSocket
from fastapi.responses import StreamingResponse, HTMLResponse

# Import service internal
from app.services.rtspReader import RTSPReader
from app.views.templates import index_html
from app.services.faceRecognition import recognizer
from app.services.mqttHelper import MQTTHelper
# from app.services.anpr import anpr_recognizer

logger = logging.getLogger(__name__)

# ➕ BARU: Pemuetaan hari (Python weekday) ke nama hari di database Anda
DAY_MAP_ID = {
    0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis",
    4: "Jumat", 5: "Sabtu", 6: "Minggu"
}

class StreamController:
    def __init__(self):
        self.RTSP_URL = "rtsp://10.115.86.180:8080/h264.sdp"
        self.reader = RTSPReader(self.RTSP_URL)

        self.last_face_data = []
        self.last_anpr_data = []
        self.last_motion = "-"
        self.last_update = None
        self.frame_width = 640
        self.frame_height = 480
        self.active_websockets = set()
        
        self.loop = None 
        self.mqtt_connected = False 
        self.analysis_counter = 0 

        # ➕ BARU: Inisialisasi Supabase Client
        self.supabase = self.init_supabase_client()
        # ➕ BARU: Ambil dan simpan jadwal kantor saat startup
        self.office_schedule = self.load_office_schedule()

        try:
            self.mqtt = MQTTHelper(client_id_prefix="ml-backend")
            logger.info("Instance MQTTHelper dibuat (belum konek).")
        except Exception as e:
            logger.error(f"Gagal membuat instance MQTT: {e}")
            self.mqtt = None

        threading.Thread(target=self.background_analysis, daemon=True).start()

    # ➕ BARU: Inisialisasi Supabase (dari models)
    def init_supabase_client(self):
        """Inisialisasi dan kembalikan Supabase client."""
        load_dotenv()
        url = os.environ.get("SUPABASE_URL")
        # PENTING: Gunakan kunci SERVICE_ROLE agar bisa 'insert' data
        key = os.environ.get("SUPABASE_KEY") 
        
        if not url or not key:
            logger.error("SUPABASE_URL/KEY tidak ditemukan. Supabase dinonaktifkan.")
            return None
        try:
            client: Client = create_client(url, key)
            logger.info("Koneksi Supabase berhasil.")
            return client
        except Exception as e:
            logger.error(f"Gagal koneksi Supabase: {e}")
            return None

    # ➕ BARU: Ambil dan proses jadwal kantor (dari timeModel)
    def load_office_schedule(self):
        """Mengambil jadwal dari tabel 'jam_kantor' dan memprosesnya."""
        if not self.supabase:
            logger.warning("Supabase non-aktif, tidak bisa mengambil jadwal kantor.")
            return {}
        try:
            nama_tabel = "jam_kantor" # Sesuai timeModel.py
            query = self.supabase.table(nama_tabel).select("*").order('id').execute()
            
            if not query.data:
                logger.warning(f"Tabel '{nama_tabel}' kosong atau tidak ditemukan.")
                return {}
            
            # Ubah jadi format yang mudah dicek: {"Senin": ("08:00", "17:00"), ...}
            schedule_dict = {}
            for item in query.data:
                # Mengacu pada React: jam_masuk, jam_pulang (bukan jam_keluar)
                hari = item.get('hari')
                masuk = item.get('jam_masuk')
                keluar = item.get('jam_pulang') # Sesuaikan jika nama kolom beda
                
                if hari and masuk and keluar:
                    # Ambil HH:MM
                    schedule_dict[hari] = (masuk[:5], keluar[:5])
            
            logger.info("Jadwal kantor berhasil diambil dan diproses.")
            return schedule_dict
        except Exception as e:
            logger.error(f"Gagal mengambil jadwal kantor: {e}")
            return {}

    # ➕ BARU: Pengecek jam kantor
    def is_office_hours(self, now: datetime):
        """Mengecek apakah waktu saat ini 'now' ada di dalam jam kantor."""
        if not self.office_schedule:
            logger.warning("Cek jam kantor dilewati, tidak ada jadwal.")
            return False # Anggap di luar jam kantor jika jadwal tidak ada

        today_name = DAY_MAP_ID.get(now.weekday())
        
        if today_name not in self.office_schedule:
            logger.info(f"Hari {today_name} tidak ada di jadwal kantor (libur).")
            return False
            
        try:
            start_str, end_str = self.office_schedule[today_name]
            
            # Ubah string "HH:MM" menjadi objek time
            start_time = dt_time.fromisoformat(start_str)
            end_time = dt_time.fromisoformat(end_str)
            current_time = now.time()
            
            # Cek apakah waktu saat ini di antara jam mulai dan selesai
            return start_time <= current_time <= end_time
        
        except Exception as e:
            logger.error(f"Error parsing jam kantor for {today_name}: {e}")
            return False

    # ➕ BARU: Helper untuk kirim log ke Supabase
    def log_to_supabase(self, table_name, data_dict):
        """Mengirim data (dict) ke tabel Supabase."""
        if not self.supabase:
            logger.warning(f"Supabase non-aktif, log ke '{table_name}' dibatalkan.")
            return
        
        try:
            # Pastikan ada 'content' jika itu nama kolom Anda
            if 'content' not in data_dict:
                logger.error("Data log harus punya key 'content'.")
                return
                
            self.supabase.table(table_name).insert(data_dict).execute()
            logger.info(f"Berhasil log ke Supabase tabel '{table_name}'.")
        except Exception as e:
            logger.error(f"Gagal log ke Supabase tabel '{table_name}': {e}")

    # ➕ BARU: Helper untuk kirim sinyal ke aktuator
    def send_actuator_mqtt(self):
        """Mengirim sinyal 'true' ke aktuator/solenoid."""
        if not self.loop or not self.mqtt or not self.mqtt_connected:
            logger.warning("MQTT koneksi belum siap. Perintah aktuator dilewati.")
            return
        
        try:
            # Mengirim '{"status": true}' dengan QOS 1
            self.loop.call_soon_threadsafe(
                lambda: self.mqtt.publish(
                    "aktuator/solenoid",
                    '{"status": true}',
                    qos=1
                )
            )
            logger.info("Perintah 'true' dikirim ke aktuator/solenoid.")
        except Exception as e:
            logger.error(f"Gagal mendelegasikan panggilan MQTT aktuator: {e}")

    # ➕ BARU: Logika inti yang diminta
    def handle_face_detection(self, face_results):
        """
        Menjalankan logika bisnis berdasarkan hasil deteksi wajah.
        Dipanggil dari thread 'background_analysis'.
        """
        if not face_results:
            return

        now = datetime.now()
        is_working_time = self.is_office_hours(now)
        current_time_str = now.strftime("%H:%M:%S")

        # Kirim log umum ke MQTT (jika masih diperlukan dari 'send_to_mqtt')
        face_labels = [f.get("label", "Unknown") for f in face_results]
        self.send_detection_log_mqtt(face_labels, []) # Mengirim log deteksi wajah ke MQTT

        for face in face_results:
            label = face.get("label", "Unknown")
            
            if label != "Unknown":
                # --- KASUS: WAJAH DIKENALI ---
                
                # 1. Selalu kirim log ke 'messages_log'
                log_msg = f"Wajah dikenali: {label} pada {now.isoformat()}"
                self.log_to_supabase('messages_log', {"content": log_msg})
                
                if is_working_time:
                    # 2a. (JAM KANTOR) Kirim sinyal MQTT ke aktuator
                    self.send_actuator_mqtt()
                else:
                    # 2b. (DI LUAR JAM KANTOR) Kirim log ke 'messages'
                    msg = f"{label} berada di kantor di luar jam kerja pukul {current_time_str}."
                    self.log_to_supabase('messages', {"content": msg})
            
            else:
                # --- KASUS: WAJAH TIDAK DIKENALI ---
                
                if not is_working_time:
                    # 1. (DI LUAR JAM KANTOR) Kirim log ke 'messages'
                    msg = f"Wajah tidak dikenal terdeteksi di luar jam kantor pukul {current_time_str}."
                    self.log_to_supabase('messages', {"content": msg})
    
    # ➕ BARU: Fungsi log MQTT (dipisah dari send_to_mqtt lama)
    def send_detection_log_mqtt(self, face_labels: list, plate_labels: list):
        """Mengirim log deteksi (wajah/plat) ke topic log MQTT."""
        if not self.loop or not self.mqtt or not self.mqtt_connected:
            return # Tidak perlu warning, ini hanya log

        log_data = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }
        if face_labels: log_data["face"] = ", ".join(face_labels)
        if plate_labels: log_data["plate"] = ", ".join(plate_labels)

        if "face" not in log_data and "plate" not in log_data:
            return # Jangan kirim log kosong

        try:
            self.loop.call_soon_threadsafe(
                lambda: self.mqtt.publish(
                    "log/deteksi/kamera1",
                    json.dumps(log_data),
                    qos=0
                )
            )
        except Exception as e:
            logger.error(f"Gagal mendelegasikan panggilan MQTT log: {e}")

    # ... (connect_mqtt, disconnect_mqtt, get_index, stream_mjpeg tetap sama) ...
    async def connect_mqtt(self):
        if self.mqtt:
            try:
                await self.mqtt.connect() 
                self.mqtt_connected = True
                logger.info("MQTT terhubung (via startup event).")
            except Exception as e:
                self.mqtt_connected = False
                logger.error(f"Gagal koneksi awal ke MQTT (startup): {e}")

    async def disconnect_mqtt(self):
        if self.mqtt and self.mqtt_connected:
            try:
                await self.mqtt.disconnect() 
                self.mqtt_connected = False
                logger.info("MQTT terputus (via shutdown event).")
            except Exception as e:
                logger.error(f"Gagal saat disconnect MQTT: {e}")

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


    # ✏️ DIUBAH: Logika dipindah ke handle_face_detection
    def background_analysis(self):
        while True:
            ret, frame = self.reader.read()
            if not ret:
                time.sleep(0.1)
                continue

            try:
                self.frame_height, self.frame_width = frame.shape[:2]
                self.analysis_counter += 1
                
                # # Jalankan ANPR (Logika ANPR tidak diubah)
                # if self.analysis_counter % 3 == 0:
                #     anpr_results = anpr_recognizer.recognize_plate(frame)
                #     if isinstance(anpr_results, list):
                #         self.last_anpr_data = anpr_results
                #         # ➕ BARU: Kirim log ANPR ke MQTT
                #         plate_labels = [p["label"] for p in anpr_results]
                #         self.send_detection_log_mqtt([], plate_labels)
                #     else:
                #         self.last_anpr_data = [] 
                
                # # Jalankan FR
                # else:
                #     face_results = recognizer.verify_face(frame)
                #     if isinstance(face_results, list):
                #         self.last_face_data = face_results
                #         self.handle_face_detection(face_results) 
                #     else:
                #         self.last_face_data = [] 

                face_results = recognizer.verify_face(frame)
                if isinstance(face_results, list):
                    self.last_face_data = face_results
                    self.handle_face_detection(face_results) 
                else:
                    self.last_face_data = [] 
                
                if self.analysis_counter > 1000:
                    self.analysis_counter = 0

                self.last_update = datetime.now(timezone.utc)
                self.push_ws_update() 

            except Exception as e:
                logger.error(f"Error analisis frame: {e}")

            time.sleep(0.1)

    # ... (push_ws_update, ws_detections tetap sama) ...
    def push_ws_update(self):
        if not self.loop: return 
            
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
                asyncio.run_coroutine_threadsafe(ws.send_text(message), self.loop)
            except Exception:
                dead_clients.append(ws)
        for ws in dead_clients:
            self.active_websockets.remove(ws)

    async def ws_detections(self, websocket: WebSocket):
        await websocket.accept()
        self.active_websockets.add(websocket)
        try:
            while True:
                await websocket.receive_text() 
        except Exception:
            self.active_websockets.remove(websocket)