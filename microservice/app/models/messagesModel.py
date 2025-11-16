import os
import time
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

def init_supabase_client():
    """
    Inisialisasi dan kembalikan Supabase client.
    """
    load_dotenv()
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise EnvironmentError("SUPABASE_URL dan SUPABASE_KEY belum di-set di .env")
        
    try:
        supabase: Client = create_client(url, key)
        return supabase
    except Exception as e:
        print(f"Error saat inisialisasi Supabase client: {e}")
        return None

def send_messages():
    supabase = init_supabase_client()
    if supabase is None:
        return

    try:
        while True:
            waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            isi_pesan = f"Pesan otomatis dari Python pada: {waktu_sekarang}"

            data_untuk_dikirim = {"content": isi_pesan}

            response = supabase.table('messages').insert(data_untuk_dikirim).execute()

            if response.data:
                print(f"[{waktu_sekarang}] BERHASIL: Mengirim '{isi_pesan}'")
            else:
                print(f"[{waktu_sekarang}] GAGAL: {response.error.message}")

            time.sleep(2)

    except KeyboardInterrupt:
        print("\nSkrip dihentikan oleh user.")
    except Exception as e:
        print(f"Terjadi error: {e}")

if __name__ == "__main__":
    send_messages()
