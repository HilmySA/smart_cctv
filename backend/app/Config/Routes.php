<?php

use CodeIgniter\Router\RouteCollection;

/**
 * @var RouteCollection
 */
$routes->get('/', 'Home::index');

$routes->group('api', ['namespace' => 'App\Controllers\Api'], function ($routes) {
    $routes->options('(:any)', static function () {
        return response()->setStatusCode(200);
    });
    $routes->get('karyawan', 'KaryawanController::index');
    $routes->post('karyawan', 'KaryawanController::create');
    $routes->get('jam-kantor', 'JamKantorController::index');
    $routes->post('jam-kantor/update', 'JamKantorController::updateBatch');
});
