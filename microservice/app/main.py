import logging
from fastapi import FastAPI
from app.routes.routes import router
from app.middleware.cors import add_cors

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

app = FastAPI()
add_cors(app)
app.include_router(router)
