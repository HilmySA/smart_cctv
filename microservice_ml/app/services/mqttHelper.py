import paho.mqtt.client as mqtt
import time
import uuid
import logging

# --- Setup logging global ---
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger("MQTTHelper")

class MQTTHelper:
    def __init__(self, client_id_prefix="python-helper"):
        self.broker = "4fcb16d24e1d40a98656703baa5331ea.s1.eu.hivemq.cloud"
        self.port = 8883
        self.username = "smart_cctv_mqtt"
        self.password = "Admin123"
        self.client_id = f"{client_id_prefix}-{uuid.uuid4()}"

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, self.client_id)
        self.client.username_pw_set(self.username, self.password)
        self.client.tls_set()
        self.client.on_connect = self._on_connect

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info("Terhubung ke broker MQTT")
        else:
            logger.error(f"Gagal terhubung (kode: {rc})")

    def connect(self):
        try:
            self.client.connect(self.broker, self.port)
            self.client.loop_start()
            # logger.info("Koneksi helper dimulai")
            time.sleep(1)  # beri waktu koneksi stabil
        except Exception as e:
            logger.exception(f"Error koneksi helper: {e}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        # logger.info("Koneksi helper ditutup")

    def publish(self, topic, message, qos=1):
        logger.info(f"Mengirim ke '{topic}' → {message}")
        result = self.client.publish(topic, message, qos=qos)
        try:
            result.wait_for_publish(timeout=3)
            if result.is_published():
                logger.info("- Pesan berhasil terkirim")
                return True
            else:
                logger.warning("- Pesan gagal (tidak terkonfirmasi)")
                return False
        except (ValueError, RuntimeError) as e:
            logger.error(f"- Gagal publish (timeout: {e})")
            return False

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
