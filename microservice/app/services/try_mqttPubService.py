import paho.mqtt.client as mqtt
import time

# --- GANTI DENGAN KREDENSIAL ANDA ---
BROKER_ADDRESS = "4fcb16d24e1d40a98656703baa5331ea.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "smart_cctv_mqtt"
PASSWORD = "Admin123"
# ------------------------------------

# ID unik untuk klien ini
CLIENT_ID = "python-ml-backend"
TOPIC = "perintah/aktuator"

# Fungsi callback saat terhubung
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Berhasil terhubung ke Broker!")
    else:
        print(f"❌ Gagal terhubung, kode: {rc}")

# Buat klien baru
# Gunakan CallbackAPIVersion.VERSION2 untuk praktik terbaik
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)

# Atur username dan password
client.username_pw_set(USERNAME, PASSWORD)

# Atur koneksi aman (TLS) - INI WAJIB UNTUK HIVEMQ CLOUD
client.tls_set()

# Atur fungsi callback
client.on_connect = on_connect

# Coba terhubung ke broker
try:
    client.connect(BROKER_ADDRESS, PORT)
except Exception as e:
    print(f"❌ Error koneksi: {e}")
    exit()

# Mulai network loop di background
client.loop_start()

# Kirim pesan (publish)
msg = "BUKA"
print(f"Mengirim pesan '{msg}' ke topik '{TOPIC}'...")

# Kirim pesan dengan QoS=1 (memastikan pesan terkirim setidaknya satu kali)
result = client.publish(TOPIC, msg, qos=1)

# Cek status pengiriman
result.wait_for_publish(timeout=5)
if result.is_published():
    print("✅ Pesan berhasil terkirim.")
else:
    print("❌ Gagal mengirim pesan.")

# Beri waktu 1 detik agar pesan pasti terkirim sebelum keluar
time.sleep(1) 

# Hentikan loop dan putuskan koneksi
client.loop_stop()
client.disconnect()
print("Koneksi terputus.")