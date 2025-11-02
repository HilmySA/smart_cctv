from fastapi.middleware.cors import CORSMiddleware

def add_cors(app):
    origins = [
    "http://localhost:5173",  # <-- Izinkan alamat frontend Vite Anda
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,       # <--- GUNAKAN DAFTAR INI
        allow_credentials=True,      # Tetap True (ini sudah benar)
        allow_methods=["*"],
        allow_headers=["*"],
    )