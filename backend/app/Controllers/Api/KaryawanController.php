<?php

namespace App\Controllers\Api;

use App\Controllers\BaseController;
use App\Models\KaryawanModel;
use Supabase\CreateClient;

class KaryawanController extends BaseController
{
    public function index()
    {
        $model = new KaryawanModel();
        return $this->response->setJSON($model->findAll());
    }

    public function create()
    {
        helper('text');

        // 1. Validasi input
        $rules = [
            'nama'   => 'required|string|max_length[255]',
            'posisi' => 'required|string|max_length[100]',
            'akses'  => 'required|in_list[Staff,Supervisor,Manager,Admin]',
            'plat'   => 'permit_empty|string|max_length[20]',
            'foto'   => [
                'label' => 'Foto Karyawan',
                'rules' => 'uploaded[foto]|is_image[foto]|mime_in[foto,image/jpg,image/jpeg,image/png]|max_size[foto,10240]',
            ],
        ];

        if (!$this->validate($rules)) {
            return $this->response
                ->setStatusCode(400)
                ->setJSON(['errors' => $this->validator->getErrors()]);
        }

        // 2. Inisialisasi Supabase
        $supabaseUrl = getenv('api_key');
        $supabaseKey = getenv('reference_id');

        if (!$supabaseUrl || !$supabaseKey) {
            return $this->response->setStatusCode(500)
                ->setJSON(['message' => 'Konfigurasi Supabase tidak ditemukan di .env']);
        }

        $supabase = new \Supabase\CreateClient($supabaseUrl, $supabaseKey);
        $storage = $supabase->storage;

        // 3. Persiapkan file
        $fotoFile = $this->request->getFile('foto');
        $namaKaryawan = $this->request->getPost('nama');
        $namaFile = url_title($namaKaryawan, '-', true) . '_' . bin2hex(random_bytes(8)) . '.' . $fotoFile->guessExtension();
        $bucket = 'smart_cctv_bucket';
        $pathDiBucket = 'known_faces/' . $namaFile;
        $fileContents = file_get_contents($fotoFile->getTempName());
        $contentType = $fotoFile->getMimeType();

        try {
            // Upload file ke Supabase
            $storage->from($bucket)->upload($pathDiBucket, $fileContents, ['contentType' => $contentType]);

            // Ambil public URL
            $publicUrlResult = $storage->from($bucket)->getPublicUrl($pathDiBucket);

            // Normalisasi ke string
            if (is_string($publicUrlResult)) {
                $publicUrl = $publicUrlResult;
            } elseif (is_object($publicUrlResult) && property_exists($publicUrlResult, 'publicURL')) {
                $publicUrl = $publicUrlResult->publicURL;
            } elseif (is_array($publicUrlResult) && isset($publicUrlResult['publicURL'])) {
                $publicUrl = $publicUrlResult['publicURL'];
            } else {
                throw new \Exception('Gagal mendapatkan public URL dari Supabase');
            }
        } catch (\Exception $e) {
            return $this->response->setStatusCode(500)
                ->setJSON(['message' => 'Supabase error: ' . $e->getMessage()]);
        }

        // 4. Simpan data ke database
        $dataDB = [
            'nama'     => $namaKaryawan,
            'posisi'   => $this->request->getPost('posisi'),
            'akses'    => $this->request->getPost('akses'),
            'plat'     => $this->request->getPost('plat'),
            'foto_url' => $publicUrl,
        ];

        $model = new \App\Models\KaryawanModel();

        try {
            $newId = $model->insert($dataDB);

            if (!$newId) {
                // Hapus file di Supabase jika gagal simpan DB
                $storage->from($bucket)->remove([$pathDiBucket]);
                return $this->response->setStatusCode(500)
                    ->setJSON(['message' => 'Gagal menyimpan data ke database.']);
            }

            // Ambil data terbaru, pastikan menjadi array
            $newKaryawan = (array) $model->find($newId);
            $newKaryawan['fotoUrl'] = $newKaryawan['foto_url'];

            return $this->response->setStatusCode(201)
                ->setJSON($newKaryawan);
        } catch (\Exception $e) {
            // Hapus file di Supabase jika terjadi exception DB
            $storage->from($bucket)->remove([$pathDiBucket]);
            return $this->response->setStatusCode(500)
                ->setJSON(['message' => 'Terjadi error saat menyimpan data: ' . $e->getMessage()]);
        }
    }
}
