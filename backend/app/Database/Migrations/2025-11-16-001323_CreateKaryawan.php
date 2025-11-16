<?php

namespace App\Database\Migrations;

use CodeIgniter\Database\Migration;

class CreateKaryawan extends Migration
{
    public function up()
    {
        $this->forge->addField([
            'id' => [
                'type'           => 'INT',
                'constraint'     => 11,
                'unsigned'       => true,
                'auto_increment' => true,
            ],
            'nama' => [
                'type'       => 'VARCHAR',
                'constraint' => '255',
            ],
            'posisi' => [
                'type'       => 'VARCHAR',
                'constraint' => '100',
            ],
            'akses' => [
                'type'       => 'VARCHAR',
                'constraint' => 20,
                'default'    => 'Staff',
            ],
            'plat' => [
                'type'       => 'VARCHAR',
                'constraint' => '20',
                'null'       => true,
            ],
            'foto_url' => [
                'type'       => 'VARCHAR',
                'constraint' => '255',
            ],
            'created_at' => [
                'type' => 'DATETIME',
                'null' => true,
            ],
            'updated_at' => [
                'type' => 'DATETIME',
                'null' => true,
            ],
        ]);
        $this->forge->addKey('id', true);
        $this->forge->createTable('karyawan');

        // Constraint diperbaiki: ganti 'tingkatan_akses' menjadi 'akses'
        $this->db->query("ALTER TABLE karyawan ADD CONSTRAINT chk_akses CHECK (akses IN ('Staff', 'Supervisor', 'Manager', 'Admin'));");
    }

    public function down()
    {
        $this->forge->dropTable('karyawan');
    }
}
