# config.py
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Muat variabel dari .env
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise EnvironmentError("Pastikan SUPABASE_URL dan SUPABASE_KEY ada di file .env")

# Buat satu instance client untuk di-import file lain
try:
    supabase: Client = create_client(url, key)
    print("Koneksi Supabase berhasil diinisialisasi.")
except Exception as e:
    print(f"Error saat inisialisasi Supabase: {e}")
    supabase = None