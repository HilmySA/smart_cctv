# faceRecognition.py

import os
import numpy as np
from PIL import Image
import face_recognition
import cv2
import io  # <-- Diperlukan untuk membaca gambar dari bytes

# Import fungsi model, BUKAN client supabase
from app.models.faceModel import get_known_faces_from_storage

class FaceRecognizer:
    def __init__(self):
        """
        Inisialisasi recognizer. Tidak lagi butuh 'known_folder'.
        Akan langsung memanggil load_known_faces().
        """
        self.known_encodings = []
        self.known_labels = []
        self.load_known_faces() # <-- Langsung panggil saat dibuat

    def load_known_faces(self):
        """
        Memuat wajah yang diketahui dari Supabase menggunakan fungsi model.
        Tidak lagi menggunakan 'folder_path'.
        """
        
        # Panggil model untuk mengambil data (label dan bytes gambar)
        known_face_data = get_known_faces_from_storage()
        
        if not known_face_data:
            print("PERINGATAN: Tidak ada data wajah yang dimuat dari Supabase.")
            return

        for label, image_bytes in known_face_data:
            try:
                # 1. Ubah bytes menjadi gambar yang bisa dibaca PIL
                image_stream = io.BytesIO(image_bytes)
                image = Image.open(image_stream).convert("RGB")
                image_np = np.array(image)

                # 2. Cari lokasi wajah
                face_locations = face_recognition.face_locations(image_np)
                
                if len(face_locations) == 0:
                    print(f"Peringatan: Tidak ada wajah terdeteksi di gambar untuk {label}, dilewati.")
                    continue

                # 3. Ambil encoding (asumsikan 1 wajah per gambar)
                encodings = face_recognition.face_encodings(image_np, face_locations)
                
                if len(encodings) > 0:
                    self.known_encodings.append(encodings[0])
                    self.known_labels.append(label)
                    print(f"Berhasil memuat encoding untuk: {label}")
                else:
                    print(f"Peringatan: Gagal membuat encoding untuk {label}, dilewati.")

            except Exception as e:
                print(f"Error memproses gambar {label}: {e}")

    # 
    # --- Metode verify_face SAMA PERSIS seperti kode Anda ---
    # --- Tidak perlu diubah sama sekali ---
    #
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
# Baris ini sekarang secara otomatis memicu koneksi ke Supabase dan memuat gambar
print("Menginisialisasi FaceRecognizer...")
recognizer = FaceRecognizer()
print("FaceRecognizer siap digunakan.")