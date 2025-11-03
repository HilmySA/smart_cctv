from fastapi import APIRouter
from app.controllers.streamController import StreamController

router = APIRouter()
controller = StreamController()

router.get("/")(controller.get_index)
router.get("/mjpeg")(controller.stream_mjpeg)
router.get("/detection/live")(controller.get_detection_data)
