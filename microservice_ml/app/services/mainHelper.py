# from mqtt_helper import MQTTHelper
# import time

# print("--- Memulai Skenario ML (Helper) ---")
# wajah_dikenali = "Andi"
# print(f"Wajah '{wajah_dikenali}' terdeteksi!")

# # 'with' akan otomatis memanggil .connect() di awal
# # dan .disconnect() di akhir
# try:
#     with MQTTHelper(client_id_prefix="ml-backend") as mqtt:
        
#         # 1. Kirim perintah ke aktuator
#         mqtt.publish("perintah/aktuator/pintu", "BUKA", qos=1)
        
#         time.sleep(0.5) # Jeda singkat
        
#         # 2. Kirim log
#         mqtt.publish("log/deteksi/kamera1", f"Wajah: {wajah_dikenali}", qos=0)
        
#         # 3. Kirim perintah lain (contoh)
#         mqtt.publish("perintah/lampu/teras", "ON", qos=0)

# except Exception as e:
#     print(f"Gagal menjalankan skenario MQTT: {e}")

# print("--- Skenario ML (Helper) Selesai ---")