import React, { useState } from 'react';
// Import icons
import {
  CameraVideo, Bell, PersonPlus, ClockHistory, Person, Briefcase,
  ShieldCheck, CarFront, Save, Broadcast, ExclamationTriangle,
  PersonCheck, People, Trash // Menambahkan icon People dan Trash
} from 'react-bootstrap-icons';

/**
 * =============================================
 * KOMPONEN UTAMA: DASHBOARD
 * =============================================
 */
export default function Dashboard() {
  
  // State notifikasi (tetap di sini)
  const [notifications, setNotifications] = useState([
    { id: 1, text: 'Motion detected at Lobby', type: 'motion' },
    { id: 2, text: 'Camera 02 offline', type: 'alert' },
  ]);

  // (STATE BARU) State daftar karyawan diangkat ke Dashboard
  const [employees, setEmployees] = useState([
    // Data contoh awal
    { id: 1, nama: 'Alice Putri', posisi: 'Manager', akses: 'Manager', plat: 'B 1 A' },
    { id: 2, nama: 'Budi Santoso', posisi: 'Software Engineer', akses: 'Staff', plat: 'D 456 B' },
  ]);

  // Fungsi untuk menambah karyawan (dikirim ke EmployeeForm)
  const handleAddEmployee = (employeeData) => {
    const newEmployee = {
      id: employees.length + 1, // (Catatan: di aplikasi nyata, gunakan ID unik)
      ...employeeData
    };
    setEmployees([...employees, newEmployee]);

    // Menambah notifikasi baru
    setNotifications([
      ...notifications,
      { id: notifications.length + 1, text: `New employee "${employeeData.nama}" added`, type: 'user' }
    ]);
  };

  // Fungsi untuk menghapus karyawan (dikirim ke EmployeeList)
  const handleDeleteEmployee = (id) => {
    const employeeToDelete = employees.find(emp => emp.id === id);
    if (window.confirm(`Yakin ingin menghapus karyawan "${employeeToDelete.nama}"?`)) {
      setEmployees(employees.filter(emp => emp.id !== id));
      // Opsi: Tambah notifikasi penghapusan
      setNotifications([
        ...notifications,
        { id: notifications.length + 1, text: `Employee "${employeeToDelete.nama}" removed`, type: 'alert' }
      ]);
    }
  };


  return (
    <div className="container-fluid p-4" style={{ backgroundColor: '#f8f9fa', minHeight: '100vh' }}>
      <div className="row g-4">
        
        {/* Kolom Utama (Kiri) */}
        <div className="col-lg-9">
          <div className="row g-4">
            
            {/* 1. Komponen Streaming CCTV */}
            <div className="col-12">
              <CCTVStream />
            </div>

            {/* (KOMPONEN BARU) 2. Daftar Karyawan */}
            <div className="col-12">
              <EmployeeList employees={employees} onDeleteEmployee={handleDeleteEmployee} />
            </div>
            
            {/* 3. Komponen Form Data Karyawan */}
            <div className="col-md-6">
              {/* Mengirim fungsi handleAddEmployee sebagai prop 'onAddEmployee' */}
              <EmployeeForm onAddEmployee={handleAddEmployee} />
            </div>
            
            {/* 4. Komponen Form Jam Masuk Kantor */}
            <div className="col-md-6">
              <ScheduleForm />
            </div>
          </div>
        </div>

        {/* Kolom Sidebar (Kanan) */}
        <div className="col-lg-3">
          {/* 5. Komponen Kolom Notifikasi */}
          <NotificationPanel notifications={notifications} />
        </div>
        
      </div>
    </div>
  );
}

/**
 * =============================================
 * 1. KOMPONEN STREAM CCTV
 * =============================================
 */
function CCTVStream() {
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
      <div className="card-body">
        <div 
          className="d-flex justify-content-center align-items-center bg-dark text-white rounded" 
          style={{ height: '300px' }} // Tinggi dikurangi sedikit
        >
          <span>[Video stream akan tampil di sini]</span>
        </div>
      </div>
    </div>
  );
}

/**
 * =============================================
 * (BARU) 2. KOMPONEN DAFTAR KARYAWAN
 * =============================================
 * Menampilkan daftar karyawan dalam bentuk tabel.
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
 * 3. KOMPONEN FORM KARYAWAN (UPDATE: Menerima Props)
 * =============================================
 */
// Menerima prop 'onAddEmployee' dari Dashboard
function EmployeeForm({ onAddEmployee }) { 
  const [nama, setNama] = useState('');
  const [posisi, setPosisi] = useState('');
  const [tingkatAkses, setTingkatAkses] = useState('Staff');
  const [platNomor, setPlatNomor] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Kirim data ke fungsi 'onAddEmployee' di komponen induk
    onAddEmployee({ 
      nama: nama, 
      posisi: posisi, 
      akses: tingkatAkses, 
      plat: platNomor 
    });
    
    // Reset form
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
 * 4. KOMPONEN FORM JAM MASUK
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
 * 5. KOMPONEN PANEL NOTIFIKASI
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
            [...notifications].reverse().map(notif => ( // Membalik urutan agar notif terbaru di atas
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