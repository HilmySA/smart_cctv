import time
import logging
from datetime import datetime, timezone
from app.services.faceRecognition import recognizer
from app.services.motionDetection import detect_movement_by_hip
from app.services.try_mqttHelper import MQTTHelper
from app.utils.image_payload import ImagePayload
from app.utils.image_utils import decode_image

logger = logging.getLogger(__name__)

def analyze_image(payload: ImagePayload):
    if not payload.image_base64:
        raise ValueError("Payload gambar tidak valid.")

    frame = decode_image(payload.image_base64)
    face_result = recognizer.verify_face(frame)
    motion_result = detect_movement_by_hip(frame)

    result = {"face": face_result, "motion": motion_result}

    if face_result != "No face detected":
        send_to_mqtt(result)

    return result

def send_to_mqtt(result):
    try:
        with MQTTHelper(client_id_prefix="ml-backend") as mqtt:
            mqtt.publish(
                "perintah/aktuator/solenoid",
                '{"status": true}', qos=1
            )
            mqtt.publish(
                "log/deteksi/kamera1",
                f'{{"face": "{result["face"]}", "motion": "{result["motion"]}", "timestamp": "{datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}"}}',
                qos=0,
            )
    except Exception as e:
        logger.error(f"Gagal menjalankan skenario MQTT: {e}")
