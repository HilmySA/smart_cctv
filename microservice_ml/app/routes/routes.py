from fastapi import APIRouter
from app.utils.image_payload import ImagePayload
from app.controllers.cameraController import analyze_image

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Server is up and running"}

@router.post("/analyze")
def analyze(payload: ImagePayload):
    return analyze_image(payload)