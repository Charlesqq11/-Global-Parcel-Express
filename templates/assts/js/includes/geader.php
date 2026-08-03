<?php
$config = require DIR . '/../config.php';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title><?= $config['title']; ?></title>

    <link rel="icon" href="<?= $config['favicon']; ?>">
    <link rel="stylesheet" href="<?= $config['stylesheet']; ?>">
</head>
<body>

<header class="header">
    <div class="container">

        <a href="index.php" class="logo">
            <img src="<?= $config['logo']; ?>" alt="Parcel Tracking System Logo" height="50">
        </a>

        <h2><?= $config['title']; ?></h2>

        <nav>
            <a href="index.php">Home</a>
            <a href="track.php">Track Parcel</a>
            <a href="dashboard.php">Dashboard</a>
            <a href="logout.php">Logout</a>
        </nav>

    </div>
</header>

<main class="container">