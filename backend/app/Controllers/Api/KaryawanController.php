<?php

namespace App\Controllers\Api;

use App\Controllers\BaseController;
use App\Models\KaryawanModel;

class KaryawanController extends BaseController
{
    /**
     * Get all karyawan
     */
    public function index()
    {
        $model = new KaryawanModel();
        return $this->response->setJSON($model->findAll());
    }

    /**
     * Create new karyawan (untuk tombol "Simpan Karyawan")
     */
    public function create()
    {
        $model = new KaryawanModel();
        
        // Ambil data JSON sebagai array asosiatif
        $data = $this->request->getJSON(true);

        // Atur aturan validasi
        $rules = [
            'nama_lengkap'    => 'required|string|max_length[255]',
            'posisi'          => 'required|string|max_length[100]',
            'tingkatan_akses' => 'required|in_list[Staff,Admin,Manager]',
            'plat_nomor'      => 'permit_empty|string|max_length[20]'
        ];

        if (!$this->validate($rules)) {
            return $this->response
                        ->setStatusCode(400)
                        ->setJSON(['errors' => $this->validator->getErrors()]);
        }

        // Data lolos validasi, simpan
        try {
            $newKaryawanId = $model->insert($data);
            
            // Periksa jika insert gagal (misal: ID tidak kembali)
            if (!$newKaryawanId) {
                 return $this->response
                            ->setStatusCode(500)
                            ->setJSON(['message' => 'Gagal menyimpan data karena alasan tidak diketahui.']);
            }

            $newKaryawan = $model->find($newKaryawanId);

            return $this->response
                        ->setStatusCode(201) // 201 Created
                        ->setJSON([
                            'message' => 'Karyawan berhasil disimpan',
                            'data' => $newKaryawan
                        ]);

        } catch (\Exception $e) {
            return $this->response
                        ->setStatusCode(500) // 500 Internal Server Error
                        ->setJSON(['message' => $e->getMessage()]);
        }
    }
}