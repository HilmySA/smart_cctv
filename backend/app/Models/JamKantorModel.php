<?php

namespace App\Models;

use CodeIgniter\Model;

class JamKantorModel extends Model
{
    protected $table            = 'jam_kantor';
    protected $primaryKey       = 'id';
    protected $useAutoIncrement = true;
    protected $returnType       = 'object';
    protected $protectFields    = true;
    protected $allowedFields    = [
        'hari',
        'jam_masuk',
        'jam_pulang'
    ];

    // Kita tidak perlu timestamps untuk tabel ini
    protected $useTimestamps = false;
}