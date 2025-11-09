<?php

namespace App\Controllers\Api;

use App\Controllers\BaseController;
use App\Models\JamKantorModel;

class JamKantorController extends BaseController
{
    /**
     * Get all 7 days schedule (untuk mengisi form di frontend)
     */
    public function index()
    {
        $model = new JamKantorModel();
        $data = $model->orderBy('id', 'ASC')->findAll();
        return $this->response->setJSON($data);
    }

    /**
     * Update 7-day schedule (untuk tombol "Simpan Jadwal")
     */
    public function updateBatch()
    {
        $model = new JamKantorModel();
        
        // Frontend harus mengirim array berisi 7 objek
        $data = $this->request->getJSON(); // Dapatkan sebagai array of objects

        if (!is_array($data) || count($data) !== 7) {
            return $this->response
                        ->setStatusCode(400)
                        ->setJSON(['message' => 'Data harus berupa array berisi 7 jadwal hari.']);
        }

        // Validasi sederhana (opsional, bisa diperketat)
        foreach ($data as $jadwal) {
            if (!isset($jadwal->hari) || !isset($jadwal->jam_masuk) || !isset($jadwal->jam_pulang)) {
                return $this->response
                            ->setStatusCode(400)
                            ->setJSON(['message' => 'Setiap item jadwal harus memiliki field hari, jam_masuk, dan jam_pulang.']);
            }
        }

        // Gunakan updateBatch untuk efisiensi
        try {
            // 'hari' adalah field yang digunakan sebagai 'where' key
            $model->updateBatch($data, 'hari');
            
            // Ambil data terbaru setelah update
            $updatedJadwal = $model->orderBy('id', 'ASC')->findAll();

            return $this->response
                        ->setStatusCode(200)
                        ->setJSON([
                            'message' => 'Jadwal berhasil diperbarui',
                            'data' => $updatedJadwal
                        ]);

        } catch (\Exception $e) {
            return $this->response
                        ->setStatusCode(500)
                        ->setJSON(['message' => $e->getMessage()]);
        }
    }
}