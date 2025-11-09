<?php

namespace App\Database\Seeds;

use CodeIgniter\Database\Seeder;

class JamKantorSeeder extends Seeder
{
    public function run()
    {
        $data = [
            ['hari' => 'Senin', 'jam_masuk' => '08:00', 'jam_pulang' => '17:00'],
            ['hari' => 'Selasa', 'jam_masuk' => '08:00', 'jam_pulang' => '17:00'],
            ['hari' => 'Rabu', 'jam_masuk' => '08:00', 'jam_pulang' => '17:00'],
            ['hari' => 'Kamis', 'jam_masuk' => '08:00', 'jam_pulang' => '17:00'],
            ['hari' => 'Jumat', 'jam_masuk' => '08:00', 'jam_pulang' => '17:00'],
            ['hari' => 'Sabtu', 'jam_masuk' => '09:00', 'jam_pulang' => '13:00'],
            ['hari' => 'Minggu', 'jam_masuk' => '00:00', 'jam_pulang' => '00:00'],
        ];

        // Using Query Builder
        $this->db->table('jam_kantor')->insertBatch($data);
    }
}