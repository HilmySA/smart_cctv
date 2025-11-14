import logging
import asyncio # ➕ TAMBAHKAN IMPORT INI
from fastapi import FastAPI
from contextlib import asynccontextmanager # ➕ TAMBAHKAN IMPORT INI

# ✏️ UBAH IMPORT INI: Tambahkan 'controller'
from app.routes.routes import router, controller 
from app.middleware.cors import add_cors

# --- Blok Konfigurasi Log Anda (Ini sudah bagus) ---
# Hapus semua handler lama (dari uvicorn)
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Tambahkan handler baru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Tambahkan handler juga ke logger uvicorn agar seragam
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.handlers = logging.root.handlers
uvicorn_logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
# --- Akhir Blok Log ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Kode ini dijalankan SAAT STARTUP
    logger.info("Menjalankan event startup...")
    try:
        # 1. Simpan event loop utama
        controller.loop = asyncio.get_event_loop() 
        # 2. Panggil method async untuk koneksi
        await controller.connect_mqtt()
        logger.info("Event startup selesai: MQTT siap.")
    except Exception as e:
        logger.error(f"Gagal saat startup event MQTT: {e}")
    
    yield # Aplikasi berjalan di sini
    
    # Kode ini dijalankan SAAT SHUTDOWN
    logger.info("Menjalankan event shutdown...")
    try:
        await controller.disconnect_mqtt()
        logger.info("Event shutdown selesai: MQTT terputus.")
    except Exception as e:
        logger.error(f"Gagal saat shutdown event MQTT: {e}")

# --- ✏️ Inisialisasi App (Ini bagian yang diperbaiki) ---

# 1. Buat app dengan lifespan HANYA SATU KALI
app = FastAPI(lifespan=lifespan)

# 2. Terapkan CORS ke app yang sudah ada
add_cors(app)

# 3. Sertakan router ke app yang sudah ada
app.include_router(router)

# ❌ HAPUS BARIS INI: app = FastAPI()