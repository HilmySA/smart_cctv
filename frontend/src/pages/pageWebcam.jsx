import React, { useRef, useState, useEffect } from "react";
import Webcam from "react-webcam";
import axios from "axios";

const App = () => {
  const webcamRef = useRef(null);
  const faceCanvasRef = useRef(null);
  const motionCanvasRef = useRef(null);
  const [result, setResult] = useState(null);
  const [debug, setDebug] = useState(""); // Menyimpan log debug

  useEffect(() => {
    const interval = setInterval(() => {
      captureAndAnalyze();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const captureAndAnalyze = async () => {
    const screenshot = webcamRef.current.getScreenshot();

    if (!screenshot) {
      console.warn("📸 Screenshot gagal diambil.");
      setDebug("❌ Screenshot gagal diambil.");
      return;
    }

    console.log("📸 Screenshot berhasil diambil.");

    try {
      const url = "http://localhost:8000/analyze";
      console.log("🌐 Mengirim POST request ke:", url);

      const res = await axios.post(url, {
        image_base64: screenshot,
      }, {
        headers: {
          "Content-Type": "application/json"
        },
            withCredentials: true, // harus sesuai dengan allow_credentials di backend
        }
      );

      console.log("✅ Response diterima:", res.data);
      setResult(res.data);
      setDebug("✅ Data berhasil dikirim dan diterima.");
    } catch (err) {
      console.error("❌ Error saat request:", err);
      setDebug(`❌ Error saat request: ${err.message}`);

      if (err.response) {
        console.error("🔻 Response error:", err.response.data);
        setDebug(`❌ Server response error: ${JSON.stringify(err.response.data)}`);
      } else if (err.request) {
        console.error("🔻 No response received. Possible CORS/Network error.");
        setDebug("❌ Tidak ada response. Mungkin error CORS atau jaringan.");
      } else {
        console.error("🔻 Request setup error:", err.message);
        setDebug(`❌ Request setup error: ${err.message}`);
      }
    }
  };

  useEffect(() => {
    const canvas = faceCanvasRef.current;
    const ctx = canvas?.getContext("2d");

    if (!canvas || !ctx || !result || !result.face) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (const face of result.face) {
      const { top, left, bottom, right, label } = face;

      ctx.beginPath();
      ctx.rect(left, top, right - left, bottom - top);
      ctx.lineWidth = 2;
      ctx.strokeStyle = "lime";
      ctx.stroke();

      ctx.font = "16px Arial";
      ctx.fillStyle = "lime";
      ctx.fillText(label, left, top - 10);
    }
  }, [result]);

  useEffect(() => {
    const canvas = motionCanvasRef.current;
    const ctx = canvas?.getContext("2d");

    if (!canvas || !ctx || !result || !result.motion) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const hip = result.motion.hip;
    if (hip) {
      ctx.beginPath();
      ctx.arc(hip.x, hip.y, 10, 0, 2 * Math.PI);
      ctx.fillStyle = "red";
      ctx.fill();

      ctx.font = "16px Arial";
      ctx.fillStyle = "red";
      ctx.fillText(result.motion.status, hip.x + 15, hip.y);
    }
  }, [result]);

  return (
    <div style={{ position: "relative", width: 640, height: 520 }}>
      <Webcam
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        width={640}
        height={480}
        videoConstraints={{ facingMode: "user" }}
      />
      <canvas
        ref={faceCanvasRef}
        width={640}
        height={480}
        style={{ position: "absolute", top: 0, left: 0 }}
      />
      <canvas
        ref={motionCanvasRef}
        width={640}
        height={480}
        style={{ position: "absolute", top: 0, left: 0 }}
      />

      <div style={{
        marginTop: 10,
        background: "#111",
        color: "#0f0",
        padding: "10px",
        fontFamily: "monospace",
        whiteSpace: "pre-wrap"
      }}>
        <strong>🧠 Motion Status:</strong> {result?.motion?.status || "Belum terdeteksi"}
        <br />
        <strong>🪵 Debug Log:</strong><br />
        {debug}
      </div>
    </div>
  );
};

export default App;