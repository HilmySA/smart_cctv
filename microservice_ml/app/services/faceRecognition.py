import os
import numpy as np
from PIL import Image
import face_recognition
import cv2

class FaceRecognizer:
    def __init__(self, known_folder):
        self.known_encodings = []
        self.known_labels = []
        self.load_known_faces(known_folder)

    def load_known_faces(self, folder_path):
        for filename in os.listdir(folder_path):
            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                path = os.path.join(folder_path, filename)
                label = os.path.splitext(filename)[0]
                image = Image.open(path).convert("RGB")
                image_np = np.array(image)

                face_locations = face_recognition.face_locations(image_np)
                if len(face_locations) == 0:
                    continue

                encodings = face_recognition.face_encodings(image_np, face_locations)
                if len(encodings) > 0:
                    self.known_encodings.append(encodings[0])
                    self.known_labels.append(label)

    def verify_face(self, frame, tolerance=0.6):
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            results = []

            for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(self.known_encodings, encoding, tolerance)
                distances = face_recognition.face_distance(self.known_encodings, encoding)

                if any(matches):
                    best_match_index = np.argmin(distances)
                    label = f"{self.known_labels[best_match_index]} ({distances[best_match_index]:.2f})"
                else:
                    label = "Unknown"

                results.append({
                    "label": label,
                    "top": top,
                    "left": left,
                    "bottom": bottom,
                    "right": right
                })

            return results if results else "No face detected"

        except Exception as e:
            return f"Error: {str(e)}"

# Inisialisasi saat modul diimpor
recognizer = FaceRecognizer("images")
