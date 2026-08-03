<?php

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

require 'vendor/autoload.php';

$mail = new PHPMailer(true);

try {
    $mail->isSMTP();
    $mail->Host = 'smtp.gmail.com';
    $mail->SMTPAuth = true;
    $mail->Username = 'your_email@gmail.com';
    $mail->Password = 'your_app_password';
    $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
    $mail->Port = 587;

    $mail->setFrom('your_email@gmail.com', 'Parcel Tracking');
    $mail->addAddress('recipient@example.com');

    $mail->Subject = 'Test Email';
    $mail->Body = 'This is a test email from PHPMailer.';

    $mail->send();
    echo "Email sent successfully!";
} catch (Exception $e) {
    echo "Message could not be sent. Error: {$mail->ErrorInfo}";
}