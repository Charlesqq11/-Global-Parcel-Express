<?php

$config = require 'config.php';

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= $config['title']; ?></title>

    <link rel="stylesheet" href="assets/css/style.css">
    <link rel="icon" href="<?= $config['favicon']; ?>">
</head>
<body>

<header>
    <div class="container">
        <img src="<?= $config['logo']; ?>" alt="Logo" height="60">
        <h1><?= $config['title']; ?></h1>
    </div>
</header>

<main class="container">

    <h2>Track Your Parcel</h2>

    <form action="track.php" method="POST">

        <label for="tracking_number">Tracking Number</label>

        <input
            type="text"
            id="tracking_number"
            name="tracking_number"
            placeholder="Enter your tracking number"
            required
        >

        <button type="submit">
            Track Parcel
        </button>

    </form>

</main>

<footer>
    <p>&copy; <?= date('Y'); ?> Parcel Tracking System. All rights reserved.</p>
</footer>

</body>
</html>