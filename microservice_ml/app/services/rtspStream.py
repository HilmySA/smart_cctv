import cv2
import threading
import time

class RTSPStream:
    def __init__(self, url, name=None, display=False, callback=None):
        """
        url: alamat RTSP
        name: nama stream (default = url)
        display: True → tampilkan via cv2.imshow()
        callback: fungsi yang menerima frame (misalnya kirim ke dashboard)
        """
        self.url = url
        self.name = name or url
        self.display = display
        self.callback = callback

        self.capture = None
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            print(f"[INFO] Stream {self.name} sudah berjalan.")
            return

        print(f"[INFO] Memulai stream dari {self.url}")
        self.capture = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
        if not self.capture.isOpened():
            print(f"[WARN] Tidak dapat membuka {self.url}")
            return

        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while self.running:
            ret, frame = self.capture.read()
            if not ret:
                print(f"[WARN] Tidak dapat membaca frame dari {self.name}")
                time.sleep(1)
                continue

            # Panggil callback kalau ada
            if self.callback:
                self.callback(self.name, frame)

            # Tampilkan window hanya jika display=True
            if self.display:
                cv2.imshow(self.name, frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.stop()
                    break

        self.release()

    def stop(self):
        self.running = False

    def release(self):
        if self.capture and self.capture.isOpened():
            self.capture.release()
        if self.display:
            try:
                cv2.destroyWindow(self.name)
            except cv2.error:
                pass
        print(f"[INFO] Stream {self.name} dihentikan.")
