from fastapi import APIRouter, WebSocket
from app.controllers.streamController import StreamController

router = APIRouter()
controller = StreamController()

@router.get("/")
def get_index():
    return controller.get_index()

@router.get("/mjpeg")
def stream_mjpeg():
    return controller.stream_mjpeg()

@router.websocket("/ws/detection")
def ws_detection(websocket: WebSocket):
    return controller.ws_detections(websocket)
