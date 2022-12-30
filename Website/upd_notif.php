<?php
$servername = "localhost";

$dbname = "id19492879_pliamdb";
$username = "id19492879_pliam";
$password = "Pli@m12112005";

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

require $_SERVER['DOCUMENT_ROOT'] . '/mail/Exception.php';
require $_SERVER['DOCUMENT_ROOT'] . '/mail/PHPMailer.php';
require $_SERVER['DOCUMENT_ROOT'] . '/mail/SMTP.php';

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
$result_last_update = $conn->query("select max(datetime) as datetime from parking_spaces");
$row_upd = $result_last_update->fetch_assoc();
$last_update = strtotime($row_upd['datetime']);
$cur_time = strtotime(gmdate("Y-m-d H:i:s"));
$dif_upd = intval(($cur_time-$last_update)/60);//in minutes
if($dif_upd > 10){
    //spam with emails
    $mail = new PHPMailer;
    $mail->isSMTP(); 
    $mail->SMTPDebug = 2; // 0 = off (for production use) - 1 = client messages - 2 = client and server messages
    $mail->Host = "smtp.gmail.com"; // use $mail->Host = gethostbyname('smtp.gmail.com'); // if your network does not support SMTP over IPv6
    $mail->Port = 587; // TLS only
    $mail->SMTPSecure = 'tls'; // ssl is deprecated
    $mail->SMTPAuth = true;
    $mail->Username = '#'; // email
    $mail->Password = '#'; // password
    $mail->setFrom('#', 'Parking Notification System'); // From email and name
    $mail->addAddress('#', 'IT'); // to email and name
    $mail->addCC('#', 'Admin');
    $mail->Subject = 'Parking System has been down for '.$dif_upd.' minutes!';
    $mail->msgHTML("Restart the parking space detection system now!"); //$mail->msgHTML(file_get_contents('contents.html'), __DIR__); //Read an HTML message body from an external file, convert referenced images to embedded,
    $mail->AltBody = 'Restart the parking space detection system now!'; // If html emails is not supported by the receiver, show this body
    // $mail->addAttachment('images/phpmailer_mini.png'); //Attach an image file
    $mail->SMTPOptions = array(
                        'ssl' => array(
                            'verify_peer' => false,
                            'verify_peer_name' => false,
                            'allow_self_signed' => true
                        )
                    );
    if(!$mail->send()){
        echo "Mailer Error: " . $mail->ErrorInfo;
    }else{
        echo "Message sent!";
    }
}
?>