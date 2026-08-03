<?php

require_once 'controllers/HomeController.php';
require_once 'controllers/AuthController.php';
require_once 'controllers/ParcelController.php';
require_once 'controllers/AdminController.php';

$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

switch ($uri) {

    case '/':
    case '/index.php':
        (new HomeController())->index();
        break;

    case '/track':
        (new ParcelController())->track();
        break;

    case '/login':
        (new AuthController())->login();
        break;

    case '/logout':
        (new AuthController())->logout();
        break;

    case '/admin/dashboard':
        (new AdminController())->dashboard();
        break;

    case '/admin/add-parcel':
        (new AdminController())->addParcel();
        break;

    case '/admin/update-parcel':
        (new AdminController())->updateParcel();
        break;

    case '/admin/delete-parcel':
        (new AdminController())->deleteParcel();
        break;

    case '/admin/export':
        (new AdminController())->export();
        break;

    case '/admin/receipt':
        (new AdminController())->receipt();
        break;

    default:
        http_response_code(404);
        echo "404 - Page Not Found";
        break;
}