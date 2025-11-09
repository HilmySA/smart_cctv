<?php

namespace App\Database\Migrations;

use CodeIgniter\Database\Migration;

class CreateJamKantor extends Migration
{
    public function up()
    {
        $this->forge->addField([
            'id' => [
                'type'           => 'INT',
                'constraint'     => 5,
                'unsigned'       => true,
                'auto_increment' => true,
            ],
            'hari' => [
                'type'       => 'VARCHAR',
                'constraint' => '10',
                'unique'     => true,
            ],
            'jam_masuk' => [
                'type' => 'TIME',
            ],
            'jam_pulang' => [
                'type' => 'TIME',
            ],
        ]);
        $this->forge->addKey('id', true);
        $this->forge->createTable('jam_kantor');
    }

    public function down()
    {
        $this->forge->dropTable('jam_kantor');
    }
}