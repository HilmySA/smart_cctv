// Import React Hooks
import React, { useState, useEffect, useRef } from "react";

// Import icons
import {
  CameraVideo,
  Bell,
  PersonPlus,
  ClockHistory,
  Person,
  Briefcase,
  ShieldCheck,
  CarFront,
  Save,
  Broadcast,
  ExclamationTriangle,
  PersonCheck,
  People,
  Trash,
  CloudUpload,
} from "react-bootstrap-icons";

// <-- BARU: Import client Supabase
import { supabase } from "../api/supabaseClient";

// =============================================
// KONFIGURASI API
// =============================================
const API_BASE_URL = "http://localhost:8080/api";

/**
 * =============================================
 * KOMPONEN UTAMA: DASHBOARD (UPDATED DENGAN API)
 * =============================================
 */
export default function Dashboard() {
  // <-- DIHAPUS: State notifikasi lokal sudah tidak diperlukan
  // const [notifications, setNotifications] = useState([...]);

  // State untuk data dari API
  const [employees, setEmployees] = useState([]);
  const [schedule, setSchedule] = useState(null);

  // State untuk loading & error
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const [employeeResponse, scheduleResponse] = await Promise.all([
          fetch(`${API_BASE_URL}/karyawan`),
          fetch(`${API_BASE_URL}/jam-kantor`),
        ]);

        if (!employeeResponse.ok || !scheduleResponse.ok) {
          throw new Error("Failed to fetch data from API");
        }

        const employeeData = await employeeResponse.json();
        const scheduleArray = await scheduleResponse.json();

        const scheduleObject = scheduleArray.reduce((acc, item) => {
          acc[item.hari] = {
            masuk: item.jam_masuk.substring(0, 5),
            keluar: item.jam_pulang.substring(0, 5),
          };
          return acc;
        }, {});

        setEmployees(employeeData);
        setSchedule(scheduleObject);

        // <-- DIHAPUS: setNotifications(...)
      } catch (err) {
        setError(err.message);
        // <-- DIHAPUS: setNotifications(...)
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleAddEmployee = async (formData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/karyawan`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to add employee.");
      }

      const newEmployee = await response.json();
      setEmployees((prev) => [...prev, newEmployee]);

      // <-- DIHAPUS: setNotifications(...)
    } catch (err) {
      setError(err.message);
      // <-- DIHAPUS: setNotifications(...)
    }
  };

  const handleDeleteEmployee = async (id) => {
    const employeeToDelete = employees.find((emp) => emp.id === id);
    if (!employeeToDelete) return;

    if (
      window.confirm(
        `Yakin ingin menghapus karyawan "${employeeToDelete.nama}"?`
      )
    ) {
      try {
        const response = await fetch(`${API_BASE_URL}/employees/${id}`, {
          method: "DELETE",
        });

        if (!response.ok) {
          throw new Error("Failed to delete employee.");
        }

        setEmployees(employees.filter((emp) => emp.id !== id));
        // <-- DIHAPUS: setNotifications(...)
      } catch (err) {
        setError(err.message);
        // <-- DIHAPUS: setNotifications(...)
      }
    }
  };

  const handleSaveSchedule = async (scheduleData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/jam-kantor/update`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(scheduleData),
      });

      if (!response.ok) {
        throw new Error("Failed to update schedule.");
      }

      const updatedSchedule = await response.json();
      setSchedule(updatedSchedule);
      // <-- DIHAPUS: setNotifications(...)
    } catch (err) {
      setError(err.message);
      // <-- DIHAPUS: setNotifications(...)
    }
  };

  // Tampilkan UI Loading atau Error
  if (loading) {
    return (
      <div
        className="d-flex justify-content-center align-items-center"
        style={{ height: "100vh" }}
      >
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading data from API...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-danger m-4">
        <h4>
          <ExclamationTriangle /> API Error
        </h4>
        <p>
          Gagal terhubung ke backend. Pastikan server API Anda berjalan di{" "}
          <strong>{API_BASE_URL}</strong>.
        </p>
        <pre>{error}</pre>
      </div>
    );
  }

  // Tampilkan Dashboard jika data berhasil dimuat
  return (
    <div
      className="container-fluid p-4"
      style={{ backgroundColor: "#f8f9fa", minHeight: "100vh" }}
    >
      <div className="row g-4">
        {/* Kolom Utama (Kiri) */}
        <div className="col-lg-9">
          <div className="row g-4">
            {/* 1. Komponen Streaming CCTV */}
            <div className="col-12">
              {/* <-- DIUBAH: Prop setNotifications dihapus */}
              <CCTVStream />
            </div>

            {/* 2. Daftar Karyawan */}
            <div className="col-12">
              <EmployeeList
                employees={employees}
                onDeleteEmployee={handleDeleteEmployee}
              />
            </div>

            {/* 3. Form Data Karyawan */}
            <div className="col-md-6">
              <EmployeeForm onAddEmployee={handleAddEmployee} />
            </div>

            {/* 4. Form Jam Masuk Kantor */}
            <div className="col-md-6">
              <ScheduleForm
                initialSchedule={schedule}
                onSaveSchedule={handleSaveSchedule}
              />
            </div>
          </div>
        </div>

        {/* Kolom Sidebar (Kanan) */}
        <div className="col-lg-3">
          {/* 5. Kolom Notifikasi */}
          {/* <-- DIUBAH: Prop notifications dihapus */}
          <NotificationPanel />
        </div>
      </div>
    </div>
  );
}

/**
 * =============================================
 * 1. KOMPONEN STREAM CCTV (DIUBAH)
 * - Prop 'setNotifications' dihapus
 * - Semua pemanggilan 'setNotifications' dihapus
 * =============================================
 */
// <-- DIUBAH: Prop { setNotifications } dihapus
function CCTVStream() {
  const [motionStatus, setMotionStatus] = useState("-");
  const imgRef = useRef(null);
  const canvasRef = useRef(null);
  const lastMotionStatus = useRef("-");
  const lastFaceCount = useRef(0);

  useEffect(() => {
    const img = imgRef.current;
    const canvas = canvasRef.current;
    if (!img || !canvas) return;

    const ctx = canvas.getContext("2d");

    function resizeCanvas() {
      canvas.width = img.clientWidth;
      canvas.height = img.clientHeight;
    }

    window.addEventListener("resize", resizeCanvas);
    img.onload = resizeCanvas;
    resizeCanvas();

    const ws = new WebSocket(`ws://localhost:8000/ws/detection`);

    ws.onopen = () => {
      console.log("WebSocket connected");
      // <-- DIHAPUS: setNotifications(...)
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
      // <-- DIHAPUS: setNotifications(...)
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      resizeCanvas();
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      if (data.faces && Array.isArray(data.faces)) {
        const scaleX = canvas.width / (data.frame_width || 640);
        const scaleY = canvas.height / (data.frame_height || 480);

        if (data.faces.length > 0 && lastFaceCount.current === 0) {
          // <-- DIHAPUS: setNotifications(...)
        }
        lastFaceCount.current = data.faces.length;

        data.faces.forEach((face) => {
          const { top, left, bottom, right, label } = face;
          const x = left * scaleX;
          const y = top * scaleY;
          const w = (right - left) * scaleX;
          const h = (bottom - top) * scaleY;

          ctx.strokeStyle = "lime";
          ctx.lineWidth = 2;
          ctx.strokeRect(x, y, w, h);
          ctx.fillStyle = "lime";
          ctx.font = "16px Arial";
          ctx.fillText(label, x + 5, y - 5);
        });
      } else {
        lastFaceCount.current = 0;
      }

      const currentMotion = data.motion || "-";
      setMotionStatus(currentMotion);

      if (currentMotion !== "-" && lastMotionStatus.current === "-") {
        // <-- DIHAPUS: setNotifications(...)
      }
      lastMotionStatus.current = currentMotion;
    };

    return () => {
      window.removeEventListener("resize", resizeCanvas);
      img.onload = null;
      ws.close();
    };
  }, []); // <-- DIUBAH: dependensi setNotifications dihapus

  return (
    <div className="card shadow-sm h-100">
      <div className="card-header d-flex justify-content-between align-items-center">
        <h5 className="mb-0">
          <CameraVideo className="me-2" style={{ verticalAlign: "middle" }} />
          CCTV Live Stream - Lobby
        </h5>
        <span className="badge bg-danger d-flex align-items-center">
          <Broadcast className="me-1" /> LIVE
        </span>
      </div>

      <div className="card-body p-0 position-relative">
        <img
          ref={imgRef}
          id="stream"
          src="http://localhost:8000/mjpeg"
          className="img-fluid rounded-top"
          alt="CCTV Stream"
          style={{ width: "100%" }}
        />
        <canvas
          ref={canvasRef}
          id="overlay"
          className="position-absolute top-0 start-0"
          style={{ pointerEvents: "none" }}
        />
      </div>

      <div className="card-footer text-muted">
        <strong>Motion Status:</strong> {motionStatus}
      </div>
    </div>
  );
}

/**
 * =============================================
 * 2. KOMPONEN DAFTAR KARYAWAN (Tidak ada perubahan)
 * =============================================
 */
function EmployeeList({ employees, onDeleteEmployee }) {
  return (
    <div className="card shadow-sm h-100">
      <div className="card-header">
        <h5 className="mb-0">
          <People className="me-2" style={{ verticalAlign: "middle" }} />
          Daftar Karyawan ({employees.length})
        </h5>
      </div>
      <div
        className="card-body"
        style={{ maxHeight: "400px", overflowY: "auto" }}
      >
        {employees.length === 0 ? (
          <p className="text-center text-muted">Belum ada data karyawan.</p>
        ) : (
          <div className="table-responsive">
            <table className="table table-hover table-striped align-middle">
              <thead
                className="table-light"
                style={{ position: "sticky", top: 0 }}
              >
                <tr>
                  <th scope="col">Foto</th>
                  <th scope="col">Nama</th>
                  <th scope="col">Posisi</th>
                  <th scope="col">Akses</th>
                  <th scope="col">Plat Nomor</th>
                  <th scope="col">Aksi</th>
                </tr>
              </thead>
              <tbody>
                {employees.map((emp) => (
                  <tr key={emp.id}>
                    <td>
                      <img
                        src={emp.fotoUrl || "https://via.placeholder.com/50"}
                        alt={emp.nama}
                        style={{
                          width: "40px",
                          height: "40px",
                          borderRadius: "50%",
                          objectFit: "cover",
                        }}
                      />
                    </td>
                    <td>{emp.nama}</td>
                    <td>{emp.posisi}</td>
                    <td>
                      <span
                        className={`badge ${
                          emp.akses === "Admin" ? "bg-danger" : "bg-secondary"
                        }`}
                      >
                        {emp.akses}
                      </span>
                    </td>
                    <td>{emp.plat || "-"}</td>
                    <td>
                      <button
                        className="btn btn-outline-danger btn-sm"
                        onClick={() => onDeleteEmployee(emp.id)}
                        title="Hapus Karyawan"
                      >
                        <Trash />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * =============================================
 * 3. KOMPONEN FORM KARYAWAN (Tidak ada perubahan)
 * =============================================
 */
function EmployeeForm({ onAddEmployee }) {
  const [nama, setNama] = useState("");
  const [posisi, setPosisi] = useState("");
  const [tingkatAkses, setTingkatAkses] = useState("Staff");
  const [platNomor, setPlatNomor] = useState("");
  const [foto, setFoto] = useState(null);
  const [fileName, setFileName] = useState("Pilih foto...");

  const handleFotoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFoto(file);
      setFileName(file.name);
    } else {
      setFoto(null);
      setFileName("Pilih foto...");
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!foto) {
      alert("Silakan upload foto diri.");
      return;
    }

    const formData = new FormData();
    formData.append("nama", nama);
    formData.append("posisi", posisi);
    formData.append("akses", tingkatAkses);
    formData.append("plat", platNomor);
    formData.append("foto", foto);

    onAddEmployee(formData);

    setNama("");
    setPosisi("");
    setTingkatAkses("Staff");
    setPlatNomor("");
    setFoto(null);
    setFileName("Pilih foto...");
    e.target.reset();
  };

  return (
    <div className="card shadow-sm h-100">
      <div className="card-header">
        <h5 className="mb-0">
          <PersonPlus className="me-2" style={{ verticalAlign: "middle" }} />
          Input Data Karyawan
        </h5>
      </div>
      <div className="card-body">
        <form onSubmit={handleSubmit}>
          {/* Form Nama */}
          <label htmlFor="nama" className="form-label">
            Nama Lengkap
          </label>
          <div className="input-group mb-3">
            <span className="input-group-text">
              <Person />
            </span>
            <input
              type="text"
              className="form-control"
              id="nama"
              value={nama}
              onChange={(e) => setNama(e.target.value)}
              placeholder="Contoh: Budi Santoso"
              required
            />
          </div>

          {/* Form Posisi */}
          <label htmlFor="posisi" className="form-label">
            Posisi
          </label>
          <div className="input-group mb-3">
            <span className="input-group-text">
              <Briefcase />
            </span>
            <input
              type="text"
              className="form-control"
              id="posisi"
              value={posisi}
              onChange={(e) => setPosisi(e.target.value)}
              placeholder="Contoh: Software Engineer"
              required
            />
          </div>

          {/* Form Tingkat Akses */}
          <label htmlFor="tingkatAkses" className="form-label">
            Tingkatan Akses
          </label>
          <div className="input-group mb-3">
            <span className="input-group-text">
              <ShieldCheck />
            </span>
            <select
              className="form-select"
              id="tingkatAkses"
              value={tingkatAkses}
              onChange={(e) => setTingkatAkses(e.target.value)}
            >
              <option value="Staff">Staff</option>
              <option value="Supervisor">Supervisor</option>
              <option value="Manager">Manager</option>
              <option value="Admin">Admin</option>
            </select>
          </div>

          {/* Form Plat Nomor */}
          <label htmlFor="platNomor" className="form-label">
            Plat Nomor (Opsional)
          </label>
          <div className="input-group mb-3">
            <span className="input-group-text">
              <CarFront />
            </span>
            <input
              type="text"
              className="form-control"
              id="platNomor"
              value={platNomor}
              onChange={(e) => setPlatNomor(e.target.value)}
              placeholder="Contoh: B 1234 XYZ"
            />
          </div>

          {/* Form Upload Foto */}
          <label htmlFor="foto" className="form-label">
            Foto Diri
          </label>
          <div className="input-group mb-3">
            <span className="input-group-text">
              <CloudUpload />
            </span>
            <input
              type="file"
              className="form-control"
              id="foto"
              accept="image/jpeg, image/png"
              onChange={handleFotoChange}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary w-100 mt-2 d-flex align-items-center justify-content-center"
          >
            <Save className="me-2" />
            Simpan Karyawan
          </button>
        </form>
      </div>
    </div>
  );
}

/**
 * =============================================
 * 4. KOMPONEN FORM JAM MASUK (Tidak ada perubahan)
 * =============================================
 */
function ScheduleForm({ initialSchedule, onSaveSchedule }) {
  const [jadwal, setJadwal] = useState(initialSchedule || {});

  useEffect(() => {
    if (initialSchedule) {
      setJadwal(initialSchedule);
    }
  }, [initialSchedule]);

  const handleTimeChange = (hari, tipe, waktu) => {
    setJadwal((prev) => ({
      ...prev,
      [hari]: {
        ...prev[hari],
        [tipe]: waktu,
      },
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSaveSchedule(jadwal);
  };

  if (Object.keys(jadwal).length === 0) {
    return (
      <div className="card shadow-sm h-100 d-flex justify-content-center align-items-center">
        <div className="spinner-border spinner-border-sm" role="status">
          <span className="visually-hidden">Loading schedule...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="card shadow-sm h-100">
      <div className="card-header">
        <h5 className="mb-0">
          <ClockHistory className="me-2" style={{ verticalAlign: "middle" }} />
          Input Jam Kantor (7 Hari)
        </h5>
      </div>
      <div className="card-body">
        <form onSubmit={handleSubmit}>
          {Object.keys(jadwal).map((hari) => (
            <div key={hari} className="row g-2 mb-2 align-items-center">
              <div className="col-3">
                <label className="form-label mb-0 fw-medium">{hari}</label>
              </div>
              <div className="col-4">
                <input
                  type="time"
                  className="form-control form-control-sm text-center"
                  aria-label={`Jam Masuk ${hari}`}
                  value={jadwal[hari].masuk}
                  onChange={(e) =>
                    handleTimeChange(hari, "masuk", e.target.value)
                  }
                  style={{ colorScheme: "light" }}
                  required
                />
              </div>
              <div className="col-1 text-center text-muted"> - </div>
              <div className="col-4">
                <input
                  type="time"
                  className="form-control form-control-sm text-center"
                  aria-label={`Jam Keluar ${hari}`}
                  value={jadwal[hari].keluar}
                  onChange={(e) =>
                    handleTimeChange(hari, "keluar", e.target.value)
                  }
                  style={{ colorScheme: "light" }}
                  required
                />
              </div>
            </div>
          ))}
          <button
            type="submit"
            className="btn btn-primary w-100 mt-3 d-flex align-items-center justify-content-center"
          >
            <Save className="me-2" />
            Simpan Jadwal
          </button>
        </form>
      </div>
    </div>
  );
}

/**
 * =============================================
 * 5. KOMPONEN PANEL NOTIFIKASI (DIUBAH)
 * - Sekarang hanya menampilkan 1 pesan terbaru
 * - Pesan baru akan menggantikan pesan lama
 * =============================================
 */
function NotificationPanel() {
  // <-- PERUBAHAN 1: State diubah dari array ke satu objek (null)
  const [message, setMessage] = useState(null);

  useEffect(() => {
    // 1. Fungsi untuk mengambil data awal (1 pesan terakhir)
    async function fetchInitialMessage() {
      const { data, error } = await supabase
        .from("messages")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(1); // <-- PERUBAHAN 2: Hanya ambil 1 data terbaru

      if (data && data.length > 0) {
        // <-- PERUBAHAN 3: Set state sebagai objek, bukan array
        setMessage(data[0]);
      } else {
        console.error("Error fetching initial message:", error);
      }
    }

    fetchInitialMessage();

    // 2. Setup subscription Real-time untuk pesan BARU
    const channel = supabase
      .channel("public:messages")
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public",
          table: "messages",
        },
        (payload) => {
          // <-- PERUBAHAN 4: Langsung GANTI state dengan pesan baru
          setMessage(payload.new);
        }
      )
      .subscribe();

    // 3. Fungsi Cleanup
    return () => {
      supabase.removeChannel(channel);
    };
  }, []); // [] = Hanya berjalan sekali saat komponen dimuat

  // Ikon default
  const getNotificationIcon = () => {
    return <Broadcast className="me-3 text-primary" size={20} />;
  };

  return (
    <div className="card shadow-sm h-100">
      <div className="card-header">
        <h5 className="mb-0">
          <Bell className="me-2" style={{ verticalAlign: "middle" }} />
          Notifikasi Real-time
        </h5>
      </div>
      <div className="card-body p-0">
        <ul
          className="list-group list-group-flush"
          // Hapus style maxHeight agar ukuran pas
        >
          {/* <-- PERUBAHAN 5: Render satu item, bukan .map() --> */}
          {message ? (
            <li
              key={message.id} // Gunakan ID dari database
              className="list-group-item list-group-item-action d-flex align-items-center"
            >
              {getNotificationIcon()}
              <span>{message.content}</span>
            </li>
          ) : (
            <li className="list-group-item text-muted">
              Menunggu notifikasi...
            </li>
          )}
        </ul>
      </div>
    </div>
  );
}
