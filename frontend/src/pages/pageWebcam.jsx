import React, { useState, useEffect, useRef } from 'react'; // Import useEffect dan useRef
// Import icons
import {
  CameraVideo, Bell, PersonPlus, ClockHistory, Person, Briefcase,
  ShieldCheck, CarFront, Save, Broadcast, ExclamationTriangle,
  PersonCheck, People, Trash
} from 'react-bootstrap-icons';

/**
 * =============================================
 * KOMPONEN UTAMA: DASHBOARD (UPDATED)
 * =============================================
 */
export default function Dashboard() {
  
  const [notifications, setNotifications] = useState([
    { id: 1, text: 'System Initialized. Waiting for connection...', type: 'alert' },
  ]);

  const [employees, setEmployees] = useState([
    { id: 1, nama: 'Alice Putri', posisi: 'Manager', akses: 'Manager', plat: 'B 1 A' },
    { id: 2, nama: 'Budi Santoso', posisi: 'Software Engineer', akses: 'Staff', plat: 'D 456 B' },
  ]);

  // (Fungsi-fungsi ini tetap sama)
  const handleAddEmployee = (employeeData) => {
    const newEmployee = { id: employees.length + 1, ...employeeData };
    setEmployees([...employees, newEmployee]);
    setNotifications(prev => [
      ...prev,
      { id: Date.now(), text: `New employee "${employeeData.nama}" added`, type: 'user' }
    ]);
  };

  const handleDeleteEmployee = (id) => {
    const employeeToDelete = employees.find(emp => emp.id === id);
    if (window.confirm(`Yakin ingin menghapus karyawan "${employeeToDelete.nama}"?`)) {
      setEmployees(employees.filter(emp => emp.id !== id));
      setNotifications(prev => [
        ...prev,
        { id: Date.now(), text: `Employee "${employeeToDelete.nama}" removed`, type: 'alert' }
      ]);
    }
  };

  return (
    <div className="container-fluid p-4" style={{ backgroundColor: '#f8f9fa', minHeight: '100vh' }}>
      <div className="row g-4">
        
        {/* Kolom Utama (Kiri) */}
        <div className="col-lg-9">
          <div className="row g-4">
            
            {/* 1. Komponen Streaming CCTV (UPDATED) */}
            <div className="col-12">
              {/* * KITA MELEMPARKAN 'setNotifications' SEBAGAI PROP
                * agar komponen CCTVStream bisa menambah notifikasi baru
              */}
              <CCTVStream setNotifications={setNotifications} />
            </div>

            {/* 2. Daftar Karyawan (Tanpa Perubahan) */}
            <div className="col-12">
              <EmployeeList employees={employees} onDeleteEmployee={handleDeleteEmployee} />
            </div>
            
            {/* 3. Form Data Karyawan (Tanpa Perubahan) */}
            <div className="col-md-6">
              <EmployeeForm onAddEmployee={handleAddEmployee} />
            </div>
            
            {/* 4. Form Jam Masuk Kantor (Tanpa Perubahan) */}
            <div className="col-md-6">
              <ScheduleForm />
            </div>
          </div>
        </div>

        {/* Kolom Sidebar (Kanan) */}
        <div className="col-lg-3">
          {/* 5. Kolom Notifikasi (Tanpa Perubahan) */}
          <NotificationPanel notifications={notifications} />
        </div>
        
      </div>
    </div>
  );
}

/**
 * =============================================
 * 1. KOMPONEN STREAM CCTV (UPDATED DENGAN LOGIKA WEBSOCKET)
 * =============================================
 */
function CCTVStream({ setNotifications }) {
  const [motionStatus, setMotionStatus] = useState('-');
  
  // Refs untuk elemen DOM (cara React untuk document.getElementById)
  const imgRef = useRef(null);
  const canvasRef = useRef(null);
  
  // Refs untuk menyimpan status sebelumnya (mencegah spam notifikasi)
  const lastMotionStatus = useRef('-');
  const lastFaceCount = useRef(0);

  // useEffect untuk setup WebSocket dan event listeners
  useEffect(() => {
    const img = imgRef.current;
    const canvas = canvasRef.current;
    if (!img || !canvas) return;

    const ctx = canvas.getContext('2d');

    // Fungsi untuk sinkronisasi ukuran canvas dengan gambar
    function resizeCanvas() {
      canvas.width = img.clientWidth;
      canvas.height = img.clientHeight;
    }

    // Event listeners untuk resize
    window.addEventListener('resize', resizeCanvas);
    img.onload = resizeCanvas;
    resizeCanvas(); // Panggil sekali saat inisialisasi

    // 🔥 Setup WebSocket
    const ws = new WebSocket(`ws://localhost:8000/ws/detection`);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setNotifications(prev => [
        ...prev,
        { id: Date.now(), text: 'CCTV stream connected', type: 'user' }
      ]);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setNotifications(prev => [
        ...prev,
        { id: Date.now(), text: 'CCTV stream disconnected', type: 'alert' }
      ]);
    };

    // 🔥 Menerima pesan dari WebSocket
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      resizeCanvas(); // Pastikan ukuran canvas selalu pas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // 1. Logika deteksi Wajah
      if (data.faces && Array.isArray(data.faces)) {
        const scaleX = canvas.width / (data.frame_width || 640);
        const scaleY = canvas.height / (data.frame_height || 480);
        
        // Notifikasi jika ada wajah baru terdeteksi
        if (data.faces.length > 0 && lastFaceCount.current === 0) {
          const label = data.faces[0].label;
          const text = label !== 'Unknown' ? `Face detected: ${label}` : 'Unknown face detected';
          setNotifications(prev => [...prev, { id: Date.now(), text: text, type: 'user' }]);
        }
        lastFaceCount.current = data.faces.length; // Update jumlah wajah

        // Gambar kotak di canvas
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
      } else {
        lastFaceCount.current = 0; // Reset jika tidak ada wajah
      }

      // 2. Logika deteksi Gerakan
      const currentMotion = data.motion || '-';
      setMotionStatus(currentMotion); // Update status di footer

      // Notifikasi jika status gerakan berubah
      if (currentMotion !== '-' && lastMotionStatus.current === '-') {
        setNotifications(prev => [...prev, { id: Date.now() + 1, text: `Motion detected: ${currentMotion}`, type: 'motion' }]);
      }
      lastMotionStatus.current = currentMotion; // Update status gerakan
    };

    // 🔥 Fungsi Cleanup: Berjalan saat komponen unmount
    return () => {
      window.removeEventListener('resize', resizeCanvas);
      img.onload = null;
      ws.close();
    };

  }, [setNotifications]); // Dependency array

  return (
    <div className="card shadow-sm h-100">
      <div className="card-header d-flex justify-content-between align-items-center">
        <h5 className="mb-0">
          <CameraVideo className="me-2" style={{ verticalAlign: 'middle' }} />
          CCTV Live Stream - Lobby
        </h5>
        <span className="badge bg-danger d-flex align-items-center">
          <Broadcast className="me-1" /> LIVE
        </span>
      </div>
      
      {/* Container untuk stream dan overlay canvas */}
      <div className="card-body p-0 position-relative">
        {/* Gambar stream MJPEG */}
        <img
          ref={imgRef}
          id="stream"
          src="http://localhost:8000/mjpeg" // Sumber gambar dari backend Anda
          className="img-fluid rounded-top"
          alt="CCTV Stream"
          style={{ width: '100%' }}
        />
        {/* Canvas untuk overlay deteksi */}
        <canvas
          ref={canvasRef}
          id="overlay"
          className="position-absolute top-0 start-0"
          style={{ pointerEvents: 'none' }} // Agar bisa klik menembus canvas
        />
      </div>
      
      <div className="card-footer text-muted">
        {/* Menampilkan status gerakan yang di-update oleh WebSocket */}
        <strong>Motion Status:</strong> {motionStatus}
      </div>
    </div>
  );
}


/**
 * =============================================
 * 2. KOMPONEN DAFTAR KARYAWAN (Tanpa Perubahan)
 * =============================================
 */
function EmployeeList({ employees, onDeleteEmployee }) {
  return (
    <div className="card shadow-sm h-100">
      <div className="card-header">
        <h5 className="mb-0">
          <People className="me-2" style={{ verticalAlign: 'middle' }} />
          Daftar Karyawan ({employees.length})
        </h5>
      </div>
      <div className="card-body" style={{ maxHeight: '400px', overflowY: 'auto' }}>
        {employees.length === 0 ? (
          <p className="text-center text-muted">Belum ada data karyawan.</p>
        ) : (
          <div className="table-responsive">
            <table className="table table-hover table-striped align-middle">
              <thead className="table-light" style={{ position: 'sticky', top: 0 }}>
                <tr>
                  <th scope="col">Nama</th>
                  <th scope="col">Posisi</th>
                  <th scope="col">Akses</th>
                  <th scope="col">Plat Nomor</th>
                  <th scope="col">Aksi</th>
                </tr>
              </thead>
              <tbody>
                {employees.map(emp => (
                  <tr key={emp.id}>
                    <td>{emp.nama}</td>
                    <td>{emp.posisi}</td>
                    <td><span className={`badge ${emp.akses === 'Admin' ? 'bg-danger' : 'bg-secondary'}`}>{emp.akses}</span></td>
                    <td>{emp.plat || '-'}</td>
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
 * 3. KOMPONEN FORM KARYAWAN (Tanpa Perubahan)
 * =============================================
 */
function EmployeeForm({ onAddEmployee }) { 
  const [nama, setNama] = useState('');
  const [posisi, setPosisi] = useState('');
  const [tingkatAkses, setTingkatAkses] = useState('Staff');
  const [platNomor, setPlatNomor] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onAddEmployee({ 
      nama: nama, 
      posisi: posisi, 
      akses: tingkatAkses, 
      plat: platNomor 
    });
    setNama('');
    setPosisi('');
    setTingkatAkses('Staff');
    setPlatNomor('');
  };

  return (
    <div className="card shadow-sm h-100">
      <div className="card-header">
        <h5 className="mb-0">
          <PersonPlus className="me-2" style={{ verticalAlign: 'middle' }} />
          Input Data Karyawan
        </h5>
      </div>
      <div className="card-body">
        <form onSubmit={handleSubmit}>
          <label htmlFor="nama" className="form-label">Nama Lengkap</label>
          <div className="input-group mb-3">
            <span className="input-group-text"><Person /></span>
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
          <label htmlFor="posisi" className="form-label">Posisi</label>
          <div className="input-group mb-3">
            <span className="input-group-text"><Briefcase /></span>
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
          <label htmlFor="tingkatAkses" className="form-label">Tingkatan Akses</label>
          <div className="input-group mb-3">
            <span className="input-group-text"><ShieldCheck /></span>
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
          <label htmlFor="platNomor" className="form-label">Plat Nomor (Opsional)</label>
          <div className="input-group mb-3">
            <span className="input-group-text"><CarFront /></span>
            <input
              type="text"
              className="form-control"
              id="platNomor"
              value={platNomor}
              onChange={(e) => setPlatNomor(e.target.value)}
              placeholder="Contoh: B 1234 XYZ"
            />
          </div>
          <button type="submit" className="btn btn-primary w-100 mt-2 d-flex align-items-center justify-content-center">
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
 * 4. KOMPONEN FORM JAM MASUK (Tanpa Perubahan)
 * =============================================
 */
function ScheduleForm() {
  const [jadwal, setJadwal] = useState({
    Senin: { masuk: '08:00', keluar: '17:00' },
    Selasa: { masuk: '08:00', keluar: '17:00' },
    Rabu: { masuk: '08:00', keluar: '17:00' },
    Kamis: { masuk: '08:00', keluar: '17:00' },
    Jumat: { masuk: '08:00', keluar: '17:00' },
    Sabtu: { masuk: '09:00', keluar: '13:00' },
    Minggu: { masuk: '00:00', keluar: '00:00' },
  });

  const handleTimeChange = (hari, tipe, waktu) => {
    setJadwal(prev => ({
      ...prev,
      [hari]: {
        ...prev[hari],
        [tipe]: waktu,
      },
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Data Jam Kantor Baru:', jadwal);
    alert('Jam kantor berhasil diperbarui!');
  };

  return (
    <div className="card shadow-sm h-100">
      <div className="card-header">
        <h5 className="mb-0">
          <ClockHistory className="me-2" style={{ verticalAlign: 'middle' }} />
          Input Jam Kantor (7 Hari)
        </h5>
      </div>
      <div className="card-body">
        <form onSubmit={handleSubmit}>
          {Object.keys(jadwal).map(hari => (
            <div key={hari} className="row g-2 mb-2 align-items-center">
              <div className="col-3">
                <label className="form-label mb-0 fw-medium">{hari}</label>
              </div>
              <div className="col-4">
                <input
                  type="time"
                  className="form-control form-control-sm"
                  aria-label={`Jam Masuk ${hari}`}
                  value={jadwal[hari].masuk}
                  onChange={(e) => handleTimeChange(hari, 'masuk', e.target.value)}
                  required
                />
              </div>
              <div className="col-1 text-center text-muted"> - </div>
              <div className="col-4">
                <input
                  type="time"
                  className="form-control form-control-sm"
                  aria-label={`Jam Keluar ${hari}`}
                  value={jadwal[hari].keluar}
                  onChange={(e) => handleTimeChange(hari, 'keluar', e.target.value)}
                  required
                />
              </div>
            </div>
          ))}
          <button type="submit" className="btn btn-primary w-100 mt-3 d-flex align-items-center justify-content-center">
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
 * 5. KOMPONEN PANEL NOTIFIKASI (Tanpa Perubahan)
 * =============================================
 */
function NotificationPanel({ notifications }) {
  
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'motion':
        return <Broadcast className="me-3 text-primary" size={20} />;
      case 'alert':
        return <ExclamationTriangle className="me-3 text-danger" size={20} />;
      case 'user':
        return <PersonCheck className="me-3 text-success" size={20} />;
      default:
        return <Bell className="me-3 text-muted" size={20} />;
    }
  };

  return (
    <div className="card shadow-sm h-100">
      <div className="card-header">
        <h5 className="mb-0">
          <Bell className="me-2" style={{ verticalAlign: 'middle' }} />
          Notifikasi
        </h5>
      </div>
      <div className="card-body p-0">
        <ul className="list-group list-group-flush" style={{ maxHeight: '80vh', overflowY: 'auto' }}>
          {notifications.length > 0 ? (
            [...notifications].reverse().map(notif => (
              <li key={notif.id} className="list-group-item list-group-item-action d-flex align-items-center">
                {getNotificationIcon(notif.type)}
                <span>{notif.text}</span>
              </li>
            ))
          ) : (
            <li className="list-group-item text-muted">
              Tidak ada notifikasi baru.
            </li>
          )}
        </ul>
      </div>
    </div>
  );
}