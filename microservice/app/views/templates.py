index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>RTSP MJPEG Stream</title>
    <style>
        body {
            background-color: #111;
            color: #eee;
            text-align: center;
            font-family: Arial, sans-serif;
        }
        h1 {
            margin-top: 10px;
        }
        #video-container {
            position: relative;
            display: inline-block;
        }
        #stream {
            border-radius: 10px;
            width: 640px;
            height: 480px;
        }
        #overlay {
            position: absolute;
            top: 0;
            left: 0;
            border-radius: 10px;
        }
        #motion-status {
            margin-top: 10px;
            font-size: 18px;
            color: #0f0;
        }
    </style>
</head>
<body>
    <h1>RTSP Stream with Live Detection</h1>
    <div id="video-container">
        <img id="stream" src="/mjpeg" />
        <canvas id="overlay" width="1280" height="720"></canvas>
    </div>
    <div id="motion-status">Motion: -</div>

    <script>
        const canvas = document.getElementById('overlay');
        const ctx = canvas.getContext('2d');
        const motionStatus = document.getElementById('motion-status');

        async function updateDetections() {
            try {
                const response = await fetch('/detection/live');
                const data = await response.json();

                ctx.clearRect(0, 0, canvas.width, canvas.height);

                if (data.faces && Array.isArray(data.faces)) {
                    data.faces.forEach(face => {
                        const { top, left, bottom, right, label } = face;

                        // Gambar bounding box
                        ctx.strokeStyle = 'lime';
                        ctx.lineWidth = 2;
                        ctx.strokeRect(left, top, right - left, bottom - top);

                        // Tampilkan label
                        ctx.fillStyle = 'lime';
                        ctx.font = '16px Arial';
                        ctx.fillText(label, left + 5, top - 8);
                    });
                }

                motionStatus.textContent = "Motion: " + (data.motion || "-");
            } catch (err) {
                console.error("Gagal ambil data deteksi:", err);
            }
        }

        // Update overlay tiap 500ms
        setInterval(updateDetections, 500);
    </script>
</body>
</html>
"""