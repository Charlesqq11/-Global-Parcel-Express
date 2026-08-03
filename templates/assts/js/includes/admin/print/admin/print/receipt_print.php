<?php

require_once '../../config/database.php';

$id = isset($_GET['id']) ? (int)$_GET['id'] : 0;

$stmt = $conn->prepare("
    SELECT *
    FROM parcels
    WHERE id = ?
");

$stmt->bind_param("i", $id);
$stmt->execute();

$result = $stmt->get_result();
$parcel = $result->fetch_assoc();

if (!$parcel) {
    die("Parcel not found.");
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Parcel Receipt</title>

<style>
body{
    font-family:Arial,sans-serif;
    margin:30px;
}

.receipt{
    max-width:700px;
    margin:auto;
    border:1px solid #000;
    padding:20px;
}

h2,h3{
    text-align:center;
}

table{
    width:100%;
    border-collapse:collapse;
    margin-top:20px;
}

td{
    padding:10px;
    border:1px solid #ccc;
}

.no-print{
    text-align:center;
    margin-bottom:20px;
}

@media print{
    .no-print{
        display:none;
    }
}
</style>

</