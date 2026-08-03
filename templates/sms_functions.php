<?php

require_once DIR . '/sms_config.php';

function sendSMS($to, $message)
{
    $config = require DIR . '/sms_config.php';

    $data = [
        'api_key'   => $config['api_key'],
        'sender_id' => $config['sender_id'],
        'to'        => $to,
        'message'   => $message,
    ];

    $ch = curl_init($config['api_url']);

    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

    $response = curl_exec($ch);

    if (curl_errno($ch)) {
        return curl_error($ch);
    }

    curl_close($ch);

    return $response;
}

?>