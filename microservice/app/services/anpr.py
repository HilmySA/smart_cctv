import easyocr
import numpy as np
import logging

logger = logging.getLogger(__name__)

class ANPRRecognizer:
    def __init__(self, lang_list=['en']):
        """
        Inisialisasi EasyOCR Reader.
        Ini akan mengunduh model saat pertama kali dijalankan.
        Ganti ['en'] dengan ['id'] jika Anda fokus pada plat Indonesia.
        """
        try:
            self.reader = easyocr.Reader(lang_list, gpu=True) # Coba gunakan GPU
            logger.info("EasyOCR (ANPR) berhasil dimuat menggunakan GPU.")
        except Exception:
            logger.warning("Gagal memuat EasyOCR di GPU, mencoba CPU...")
            self.reader = easyocr.Reader(lang_list, gpu=False) # Fallback ke CPU
            logger.info("EasyOCR (ANPR) berhasil dimuat menggunakan CPU.")
            
        self.confidence_threshold = 0.4 # Ambil teks dengan confidence di atas 40%

    def recognize_plate(self, frame):
        """
        Mendeteksi dan mengenali plat nomor dari satu frame.
        Mengembalikan format yang mirip dengan FaceRecognizer.
        """
        try:
            # EasyOCR bekerja dengan channel warna BGR (default OpenCV)
            results = self.reader.readtext(frame)
            
            formatted_results = []

            for (bbox, text, prob) in results:
                if prob < self.confidence_threshold:
                    continue

                # Bersihkan teks plat nomor (huruf besar, tanpa spasi)
                clean_text = text.upper().replace(' ', '')
                
                # bbox adalah list 4 titik [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                # Kita ubah ke format (top, right, bottom, left)
                # Dapatkan bounding box lurus, bukan 4 titik
                (tl, tr, br, bl) = bbox
                top = int(tl[1])
                left = int(tl[0])
                bottom = int(br[1])
                right = int(br[0])

                label = f"{clean_text} ({prob:.2f})"

                formatted_results.append({
                    "label": label,
                    "top": top,
                    "left": left,
                    "bottom": bottom,
                    "right": right
                })

            return formatted_results if formatted_results else "No plate detected"

        except Exception as e:
            logger.error(f"Error saat ANPR: {e}")
            return f"Error: {str(e)}"

# Inisialisasi saat modul diimpor (sama seperti recognizer)
# Kita buat satu instance untuk digunakan di seluruh aplikasi
anpr_recognizer = ANPRRecognizer()