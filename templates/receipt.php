<?php

require_once 'db.php';

$id = $_GET['id'] ?? 0;

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
<html>
<head>
    <meta charset="UTF-8">
    <title>Parcel Receipt</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
        }
        .receipt {
            max-width: 700px;
            margin: auto;
            border: 1px solid #ccc;
            padding: 20px;
        }
        h2 {
            text-align: center;
        }
        table {
            width: 100%;
        }
        td {
            padding: 8px;
            border-bottom: 1px solid #ddd;
        }
        .print {
            margin-top: 20px;
            text-align: center;
        }
    </style>
</head>
<body>

<div class="receipt">

    <h2>Parcel Tracking Receipt</h2>

    <table>
        <tr>
            <td><strong>Tracking Number</strong></td>
            <td><?= htmlspecialchars($parcel['tracking_number']) ?></td>
        </tr>

        <tr>
            <td><strong>Sender</strong></td>
            <td><?= htmlspecialchars($parcel['sender_name']) ?></td>
        </tr>

        <tr>
            <td><strong>Receiver</strong></td>
            <td><?= htmlspecialchars($parcel['receiver_name']) ?></td>
        </tr>

        <tr>
            <td><strong>Status</strong></td>
            <td><?= htmlspecialchars($parcel['status']) ?></td>
        </tr>

        <tr>
            <td><strong>Location</strong></td>
            <td><?= htmlspecialchars($parcel['location']) ?></td>
        </tr>

        <tr>
            <td><strong>Updated At</strong></td>
            <td><?= htmlspecialchars($parcel['updated_at']) ?></td>
        </tr>
    </table>

    <div class="print">
        <button onclick="window.print()">Print Receipt</button>
    </div>

</div>

</body>
</html>