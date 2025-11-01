import paho.mqtt.client as mqtt

# --- GANTI DENGAN KREDENSIAL ANDA ---
BROKER_ADDRESS = "4fcb16d24e1d40a98656703baa5331ea.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "smart_cctv_mqtt"
PASSWORD = "Admin123"
# ------------------------------------

CLIENT_ID = "ml-backend"
TOPIC = "perintah/aktuator/solenoid" # Topik yang sama dengan publisher

# Fungsi callback saat terhubung
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Berhasil terhubung ke Broker!")
        # Langsung subscribe ke topik setelah terhubung
        client.subscribe(TOPIC, qos=1)
        print(f"Mendengarkan topik: '{TOPIC}'")
    else:
        print(f"❌ Gagal terhubung, kode: {rc}")

# Fungsi callback saat PESAN DITERIMA
def on_message(client, userdata, msg):
    # Dekode pesan dari byte menjadi string
    pesan_diterima = msg.payload.decode()
    print(f"\n📨 Pesan Diterima!")
    print(f"   Topik   : {msg.topic}")
    print(f"   Pesan   : {pesan_diterima}")
    
    # --- Di sinilah Anda menggerakkan aktuator ---
    if pesan_diterima == "BUKA":
        print("🚀 Aksi: Menggerakkan aktuator untuk MEMBUKA!")
    elif pesan_diterima == "TUTUP":
        print("🔒 Aksi: Menggerakkan aktuator untuk MENUTUP!")
    # ----------------------------------------------

# Buat klien baru
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)

# Atur username dan password
client.username_pw_set(USERNAME, PASSWORD)

# Atur koneksi aman (TLS) - WAJIB
client.tls_set()

# Atur fungsi callback
client.on_connect = on_connect
client.on_message = on_message

# Coba terhubung ke broker
try:
    client.connect(BROKER_ADDRESS, PORT)
except Exception as e:
    print(f"❌ Error koneksi: {e}")
    exit()

print("Menunggu pesan... (Tekan CTRL+C untuk berhenti)")
client.loop_forever()