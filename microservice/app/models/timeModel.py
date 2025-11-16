import os
from dotenv import load_dotenv
from supabase import create_client, Client

def init_supabase_client():
    """
    Inisialisasi dan kembalikan Supabase client.
    
    Memuat variabel dari file .env.
    """
    # Muat variabel dari .env
    load_dotenv()
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise EnvironmentError("SUPABASE_URL dan SUPABASE_KEY belum di-set di .env")
        
    try:
        # Buat client Supabase
        supabase: Client = create_client(url, key)
        return supabase
    except Exception as e:
        print(f"Error saat inisialisasi Supabase client: {e}")
        return None

def get_jadwal_kantor(supabase_client: Client):
    """
    Model untuk mengambil data jadwal kantor dari Supabase.
    
    Asumsi nama tabel: 'jadwal_kantor'
    Asumsi kolom urutan: 'id'
    """
    if not supabase_client:
        print("Supabase client tidak valid.")
        return None, "Supabase client tidak valid."

    try:
        # 1. Tentukan nama tabel
        nama_tabel = "jam_kantor"
        
        # 2. Buat query
        #    - select('*') mengambil semua kolom
        #    - order('id') mengurutkan berdasarkan kolom 'id'. Ganti jika perlu.
        query = supabase_client.table(nama_tabel).select("*").order('id').execute()
        
        # 3. Cek hasil data
        if query.data:
            return query.data, None  # Kembalikan data dan tidak ada error
        else:
            # Ini bisa terjadi jika tabel kosong atau ada error (misal, tabel tidak ada)
            error_message = query.error.message if query.error else "Tidak ada data ditemukan."
            print(f"Info: {error_message}")
            return None, error_message

    except Exception as e:
        print(f"Terjadi error saat mengambil data: {e}")
        return None, str(e)

# --- Contoh Penggunaan ---
if __name__ == "__main__":
    
    # 1. Inisialisasi client
    client = init_supabase_client()
    
    if client:
        print("Berhasil terhubung ke Supabase. Mengambil data...")
        
        # 2. Panggil model untuk ambil data
        data_jadwal, error = get_jadwal_kantor(client)
        
        if data_jadwal:
            print("\n--- 🟢 Data Jadwal Berhasil Diambil ---")

            for item in data_jadwal:
                print(item)
            
        else:
            print(f"\n--- 🔴 Gagal mengambil data ---")
            print(f"Error: {error}")