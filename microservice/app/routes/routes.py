from fastapi import APIRouter
from app.utils.image_payload import ImagePayload
from app.controllers.cameraController import analyze_image
from app.controllers.streamController import StreamController

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Server is up and running"}

@router.post("/analyze")
def analyze(payload: ImagePayload):
    return analyze_image(payload)

controller = StreamController()
router.get("/")(controller.get_index)
router.get("/mjpeg")(controller.stream_mjpeg)
