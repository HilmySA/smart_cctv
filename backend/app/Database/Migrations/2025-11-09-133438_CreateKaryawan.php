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
            'nama_lengkap' => [
                'type'       => 'VARCHAR',
                'constraint' => '255',
            ],
            'posisi' => [
                'type'       => 'VARCHAR',
                'constraint' => '100',
            ],
            'tingkatan_akses' => [
                'type'       => 'VARCHAR',
                'constraint' => 20,
                'default'    => 'Staff',
            ],
            'plat_nomor' => [
                'type'       => 'VARCHAR',
                'constraint' => '20',
                'null'       => true,
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
        $this->db->query("ALTER TABLE karyawan ADD CONSTRAINT chk_tingkatan_akses CHECK (tingkatan_akses IN ('Staff', 'Admin', 'Manager'));");
    }

    public function down()
    {
        $this->forge->dropTable('karyawan');
    }
}
