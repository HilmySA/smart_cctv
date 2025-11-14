import gmqtt
import logging
import uuid
import ssl
import asyncio  # Pastikan ini diimpor

logger = logging.getLogger(__name__)

class MQTTHelper:
    def __init__(self, client_id_prefix="python-gmqtt"):
        self.broker = "4fcb16d24e1d40a98656703baa5331ea.s1.eu.hivemq.cloud"
        self.port = 8883
        self.username = "smart_cctv_mqtt"
        self.password = "Admin123"
        self.client_id = f"{client_id_prefix}-{uuid.uuid4()}"

        self.client = gmqtt.Client(self.client_id)
        self.client.set_auth_credentials(self.username, self.password)

        self.client.set_config({
            'reconnect_retries': -1,  # Biarkan gmqtt menangani auto-reconnect
            'reconnect_delay': 5
        })

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_subscribe = self._on_subscribe
        logger.info("gmqtt Client diinisialisasi.")

    def _on_connect(self, client, flags, rc, properties):
        logger.info(f"Terhubung ke broker MQTT (kode: {rc})")

    def _on_disconnect(self, client, packet, exc=None):
        logger.warning("Koneksi MQTT terputus. Menunggu auto-reconnect...")

    def _on_subscribe(self, client, mid, qos, properties):
        logger.info(f"Berhasil subscribe (MID={mid})")

    # ❗️ DIUBAH: Jadikan method ini ASYNC
    async def connect(self):
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            # ❌ HAPUS SEMUA LOGIKA EVENT LOOP MANUAL
            # loop = asyncio.new_event_loop()
            # asyncio.set_event_loop(loop)
            # loop.run_until_complete(...)

            # ✅ CUKUP AWAIT KONEKSI CLIENT.
            # Ini akan berjalan di dalam event loop FastAPI.
            await self.client.connect(self.broker, self.port, ssl=ssl_context)
            
            # Kita tidak perlu log "Koneksi dimulai" di sini, 
            # biarkan callback _on_connect yang menanganinya.
            
        except Exception as e:
            logger.error(f"Gagal terhubung ke MQTT: {e}")
            raise  # Lempar error agar controller tahu

    # ❗️ DIUBAH: Jadikan method ini ASYNC
    async def disconnect(self):
        try:
            # ❌ HAPUS SEMUA LOGIKA EVENT LOOP MANUAL
            
            # ✅ CUKUP AWAIT DISCONNECT
            await self.client.disconnect()
            logger.info("Koneksi MQTT ditutup.")
        except Exception as e:
            logger.error(f"Gagal disconnect MQTT: {e}")

    # ❗️ DIUBAH: Jadikan method ini ASYNC
    def publish(self, topic, message, qos=1):
        try:
            logger.info(f"Mengirim ke '{topic}' → {message}")
            
            # ✅ AWAIT PUBLISH DARI CLIENT
            # Ini akan cocok dengan panggilan 'await self.mqtt.publish' di controller
            self.client.publish(topic, message, qos=qos)
            
        except Exception as e:
            logger.error(f"Gagal publish (error: {e})")