<?php

// Update parcel status in database
$stmt = $conn->prepare("
    UPDATE parcels
    SET status = ?, updated_at = NOW()
    WHERE id = ?
");

if ($stmt) {

    $stmt->bind_param("si", $status, $id);

    if ($stmt->execute()) {
        echo "Parcel status updated successfully.";
    } else {
        echo "Error updating parcel status: " . $stmt->error;
    }

    $stmt->close();

} else {
    echo "Prepare failed: " . $conn->error;
}

?>