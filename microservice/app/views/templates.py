index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>RTSP MJPEG Stream (WebSocket Realtime)</title>
    <style>
        body {
            background-color: #111;
            color: #eee;
            text-align: center;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }
        h1 { margin-top: 10px; }
        #video-container {
            position: relative;
            display: inline-block;
        }
        #stream {
            border-radius: 10px;
            max-width: 90vw;
            height: auto;
        }
        #overlay {
            position: absolute;
            top: 0; left: 0;
            border-radius: 10px;
            pointer-events: none;
        }
        #motion-status {
            margin-top: 10px;
            font-size: 18px;
            color: #0f0;
        }
    </style>
</head>
<body>
    <h1>RTSP Stream with WebSocket Detection</h1>
    <div id="video-container">
        <img id="stream" src="/mjpeg" />
        <canvas id="overlay"></canvas>
    </div>
    <div id="motion-status">Motion: -</div>

    <script>
        const streamImg = document.getElementById('stream');
        const canvas = document.getElementById('overlay');
        const ctx = canvas.getContext('2d');
        const motionStatus = document.getElementById('motion-status');

        function resizeCanvas() {
            canvas.width = streamImg.clientWidth;
            canvas.height = streamImg.clientHeight;
        }

        window.addEventListener('resize', resizeCanvas);
        streamImg.onload = resizeCanvas;

        // 🔥 WebSocket realtime update
        const ws = new WebSocket(`ws://${location.host}/ws/detection`);

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            resizeCanvas();
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if (data.faces && Array.isArray(data.faces)) {
                const scaleX = canvas.width / (data.frame_width || 640);
                const scaleY = canvas.height / (data.frame_height || 480);

                data.faces.forEach(face => {
                    const { top, left, bottom, right, label } = face;
                    const x = left * scaleX;
                    const y = top * scaleY;
                    const w = (right - left) * scaleX;
                    const h = (bottom - top) * scaleY;

                    ctx.strokeStyle = 'lime';
                    ctx.lineWidth = 2;
                    ctx.strokeRect(x, y, w, h);
                    ctx.fillStyle = 'lime';
                    ctx.font = '16px Arial';
                    ctx.fillText(label, x + 5, y - 5);
                });
            }

            motionStatus.textContent = "Motion: " + (data.motion || "-");
        };
    </script>
</body>
</html>
"""
