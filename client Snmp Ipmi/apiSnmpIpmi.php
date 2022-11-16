<?php

// API for retrieve Snmp_Ipmi application data
// The data are stored in a MySql database
header('Content-Type: application/json');

// Connection to the database
function init_db() {
  try {
    // Database connection string
  	return new PDO('mysql:host=localhost;dbname=Snmp_Ipmi;', 'samsamTest', 'Password');
  } catch(Exception $e) {
  	exit('{"status":"error","code":"501","reason":"ERROR PARAMETERS DB"}'); // Invalid DB connection parameters
  }
}

// Insert the SNMP data of the Snmp_Ipmi client, in the BDD
function insert_snmp($db, $item){
        $request = $db->prepare("INSERT INTO snmp (server_name, metric_name, metric_value, metric_oid, timestamp) VALUES (:server_name, :metric_name, :metric_value, :metric_oid, :timestamp)");
        $request->bindValue(":server_name",$item["server_name"], PDO::PARAM_STR);
        $request->bindValue(":metric_name",$item["name"],PDO::PARAM_STR);
        $request->bindValue(":metric_value",$item["value"],PDO::PARAM_STR);
        $request->bindValue(":metric_oid",$item["oid"],PDO::PARAM_STR);
        $request->bindValue(":timestamp",time(),PDO::PARAM_STR);

        if ($request->execute() === true){
                return true;
        }
        else {
                return false;
        }
}

// Insert the IPMI data of the Snmp_Ipmi client, in the database
function insert_ipmi($db, $item){
        $request = $db->prepare("INSERT INTO  ipmi (server_name, metric_name, metric_value, timestamp) VALUES (:server_name, :metric_name, :metric_value, :timestamp)");
        $request->bindValue(":server_name",$item["server_name"],PDO::PARAM_STR);
        $request->bindValue(":metric_name",$item["name"],PDO::PARAM_STR);
        $request->bindValue(":metric_value",$item["value"],PDO::PARAM_STR);
        $request->bindValue(":timestamp",time(),PDO::PARAM_STR);

        if ($request->execute() === true){
                return true;
        }
        else {
                return false;
        }
}
// Decode the json string from the Snmp_Ipmi client and place it in the parsed_json variable
$parsed_json = json_decode(file_get_contents('php://input'),true);
$snmp_presence = false;
$ipmi_presence = false;

// Verification of received data
if (is_array($parsed_json)){
        if(array_key_exists("SNMP",$parsed_json)){
                $snmp_presence = true;
        }
        if(array_key_exists("IPMI",$parsed_json)){
                $ipmi_presence = true;
        }
}
else {
        exit('{"status":"error","code":"502","reason":"error no valid data found"}'); // Invalid Json
}

// Whether SNMP data or IPMI data are presents
if ($snmp_presence || $ipmi_presence){
        $db = init_db();
        if ($snmp_presence){
                foreach($parsed_json["SNMP"] as $item){
                        if (insert_snmp($db, $item) === false){
                                exit('{"status":"error","code":"503","reason":"error snmp data"}');
                        }
                }
        }
        if ($ipmi_presence){
                foreach($parsed_json["IPMI"] as $item){
                        if (insert_ipmi($db, $item) === false){
                                exit('{"status":"error","code":"503","reason":"error ipmi data"}');
                        }
                }
        }
}

?>
