# model.py
from app.config.config import supabase # Import client dari config.py
import os

# Tentukan nama bucket dan folder Anda di Supabase Storage
BUCKET_NAME = "smart_cctv_bucket" # <-- Diperbarui
FOLDER_PATH = "known_faces"       # <-- Ditambahkan

def get_known_faces_from_storage():
    """
    Mengambil daftar semua file gambar dari folder spesifik
    di Supabase Storage dan mengunduh kontennya.

    Mengembalikan:
        list: Daftar tuple, setiap tuple berisi (label, image_bytes)
    """
    if supabase is None:
        print("Error: Klien Supabase tidak terinisialisasi.")
        return []

    try:
        # 1. List semua file di dalam bucket DAN folder
        print(f"Mengakses bucket: {BUCKET_NAME}, path: {FOLDER_PATH}...")
        files = supabase.storage.from_(BUCKET_NAME).list(path=FOLDER_PATH) # <-- Ditambahkan path
        
        if not files:
            print(f"Peringatan: Tidak ada file yang ditemukan di {BUCKET_NAME}/{FOLDER_PATH}")
            return []

        face_data_list = []
        
        for file_item in files:
            file_name = file_item.get('name')
            
            # Lewati file/folder sistem (misal: .emptyFolderPlaceholder)
            if not file_name or file_name.startswith('.'):
                continue
                
            # 2. Ambil label dari nama file (misal: "nama_orang.jpg" -> "nama_orang")
            label = os.path.splitext(file_name)[0]
            
            # 3. Buat path lengkap file untuk diunduh
            full_file_path = f"{FOLDER_PATH}/{file_name}"
            
            try:
                # 4. Download konten file (dalam bentuk bytes) menggunakan path lengkap
                print(f"Mengunduh data untuk: {label} (dari {full_file_path})...")
                image_bytes = supabase.storage.from_(BUCKET_NAME).download(full_file_path) # <-- Diperbarui
                
                if image_bytes:
                    face_data_list.append((label, image_bytes))
                
            except Exception as download_error:
                print(f"Gagal mengunduh {full_file_path}: {download_error}")

        print(f"Berhasil memuat {len(face_data_list)} data wajah dari Supabase.")
        return face_data_list
        
    except Exception as e:
        print(f"Error mengambil daftar file dari Supabase Storage ({BUCKET_NAME}/{FOLDER_PATH}): {e}")
        return []