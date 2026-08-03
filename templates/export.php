<?php

require_once 'db.php';

header('Content-Type: text/csv');
header('Content-Disposition: attachment; filename="parcels.csv"');

$output = fopen('php://output', 'w');

fputcsv($output, [
    'ID',
    'Tracking Number',
    'Sender',
    'Receiver',
    'Status',
    'Location',
    'Updated At'
]);

$sql = "SELECT id, tracking_number, sender_name, receiver_name, status, location, updated_at
        FROM parcels
        ORDER BY updated_at DESC";

$result = $conn->query($sql);

if ($result && $result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        fputcsv($output, $row);
    }
}

fclose($output);
$conn->close();

exit;
?>