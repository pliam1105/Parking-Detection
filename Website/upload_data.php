<?php 
$servername = "localhost";

$dbname = "id19492879_pliamdb";
$username = "id19492879_pliam";
$password = "Pli@m12112005";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} 

$inputJSON = file_get_contents('php://input');
$input= json_decode( $inputJSON ); 
$park_id = $input[0];
$res_id=$conn->query("select max(entry_id) as max_id from parking_spaces where parking_id=".$park_id);
$cur_id=$res_id->fetch_assoc()["max_id"]+1;
//var_dump($cur_id)
for($i=1;$i<count($input);$i++){
    $free=$input[$i];
    $sql="insert into parking_spaces (parking_id,entry_id,space_id,is_empty) values(".$park_id.",".$cur_id.",".$i.",".($free?"true":"false").")";
    echo $sql."<br>";
    $res=$conn->query($sql);
    if(!$res===TRUE){
        echo "Error: " . $sql . "<br>" . $conn->error; 
        exit();
    }
}
$conn->close();
?>