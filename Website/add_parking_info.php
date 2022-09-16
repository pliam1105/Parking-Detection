<?php 
//Program to write moisture sensor measurements with esp32 via php

$servername = "localhost";

// REPLACE with your Database name
$dbname = "id19492879_pliamdb";
// REPLACE with Database user
$username = "id19492879_pliam";
// REPLACE with Database user password
$password = "Pli@m12112005";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} 

$sql = file_get_contents('php://input');;
echo $sql."\n";
$res=$conn->query($sql);
if(!$res===TRUE){
    echo "Error: " . $sql . "\n" . $conn->error; 
}
$conn->close();
?>