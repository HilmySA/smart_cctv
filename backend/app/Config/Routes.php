<?php

use CodeIgniter\Router\RouteCollection;

/**
 * @var RouteCollection $routes
 */
$routes->get('/', 'Home::index');

$routes->group('api', ['namespace' => 'App\Controllers\Api'], function ($routes) {
    $routes->get('karyawan', 'KaryawanController::index');
    $routes->post('karyawan', 'KaryawanController::create');
    $routes->get('jam-kantor', 'JamKantorController::index');
    $routes->post('jam-kantor/update', 'JamKantorController::updateBatch');
});