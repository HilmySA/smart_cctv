#MICROSERVICE ML

1. Buat environment conda dengan mamba dan install

- mamba env create -f environment.yml
- mamba activate condaenv

3. Install yang hanya ada di pip PiPy

- pip install "C:\Hilmy\Kuliah\Belajar mandiri\smart_cctv\microservice_ml\library\dlib-19.24.1-cp310-cp310-win_amd64.whl"
- pip install lainnya

4. Intall gstreamer dari webnya versi runtim cmsxv
5. Jalankan uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
6. python -m app.main

#FRONTEND

- npm run dev

#CONDA

- mamba env create -f environment.yml
- mamba env update -f environment.yml
- mamba activate condaenv
- conda deactivate

#RUN GSTREAMER
gst-launch-1.0.exe rtspsrc location=rtsp://10.15.221.182:8080/h264.sdp latency=0 ! rtph264depay ! avdec_h264 ! videoconvert ! video/x-raw,format=BGR ! tcpserversink host=127.0.0.1 port=5000
