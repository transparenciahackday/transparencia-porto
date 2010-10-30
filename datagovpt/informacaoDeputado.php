<?php 

ob_implicit_flush(1);
ob_start();

define('DB_CHARSET', 'utf8');

$host = "localhost";
$username = "oportoem_sfognab";
$password = "0ru8Na;@7QgV";
$db = "oportoem_datagovpt";
$con_host = @mysql_connect($host,$username,$password);
$con_db = @mysql_select_db($db,$conexao_host );
mysql_connect($host,$username,$password) or die ("Não pude conectar: " . mysql_error());

//log
logAccess();

$key = $_GET['key'] ;
if ($key == '') {
	die('invalid key');
} else {
	$hashkey = array("QQOPD4VzmHL4yhr", "qvdJjQnYp9k8RER", "HFRTO12CQevyDwT", "APWvPvJTtvmCdx1", "B1Ew1iA6AiSLo9B", "FQjfWAj0QoXsFnQ", "h12xTrbe4R8JUbG", "jlkMl05mJZKHgat", "uodt4Pwhazr3EvJ", "ynvNn5JdMzPrMlm", "tJTVeE4BgxkUWk7");
	if (in_array($key, $hashkey) == false) {
		die('invalid key');
	}
}

$legislatura = $_GET['legislatura'] ;
$mpid = $_GET['mpid'] ;
$opcao = $_GET['opcao'] ;

if ($opcao == '') die('opção inválida');
switch ($opcao) {
	case 'MP':
		if ($legislatura == '') {
			$result = mysql_query("SELECT m.MPID, m.Name, m.DateOfBirth, m.Occupation FROM oportoem_datagovpt.MP m order by m.MPID");
		} else {
			$result = mysql_query("SELECT m.MPID, m.Name, m.DateOfBirth, m.Occupation FROM oportoem_datagovpt.MP as m INNER JOIN oportoem_datagovpt.Caucus as c ON m.mpid = c.mpid WHERE c.caucusid =  '" . $legislatura . "' ORDER BY MPID");
		}; break;
	case 'Caucus':
		if ($legislatura == '') {
			$result = mysql_query("SELECT c.ID, c.MPID, c.CaucusID, c.Dates, c.Constituency, c.Party, c.HasActivity, c.HasRegistoInteresses, m.Name, m.DateOfBirth, m.Occupation FROM oportoem_datagovpt.Caucus c INNER JOIN oportoem_datagovpt.MP m ON c.mpid = m.mpid order by c.MPID");
		} else {
			$result = mysql_query("SELECT c.ID, c.MPID, c.CaucusID, c.Dates, c.Constituency, c.Party, c.HasActivity, c.HasRegistoInteresses, m.Name, m.DateOfBirth, m.Occupation FROM oportoem_datagovpt.Caucus c INNER JOIN oportoem_datagovpt.MP m ON c.mpid = m.mpid WHERE c.CaucusID =  '" . $legislatura . "' ORDER BY c.MPID");
		}; break;
	case 'CaucusInfo':
		$result = mysql_query("SELECT DISTINCT CaucusID, Dates FROM oportoem_datagovpt.Caucus ORDER BY CaucusID");	
		break;
	case 'FactsType':
		$result = mysql_query("SELECT DISTINCT FactType FROM oportoem_datagovpt.Facts ORDER BY FactType");	
		break;
	case 'Facts':
		if ($legislatura == '') {
			if ($mpid == '') {
				$result = mysql_query("SELECT f.ID, f.MPID, f.FactType, f.Value, m.Name, m.DateOfBirth, m.Occupation FROM  oportoem_datagovpt.Facts f  INNER JOIN oportoem_datagovpt.MP m ON f.mpid = m.mpid INNER JOIN oportoem_datagovpt.Caucus c ON m.mpid = c.mpid order by MPID, FactType");
			} else {
				$result = mysql_query("SELECT f.ID, f.MPID, f.FactType, f.Value, m.Name, m.DateOfBirth, m.Occupation FROM  oportoem_datagovpt.Facts f  INNER JOIN oportoem_datagovpt.MP m ON f.mpid = m.mpid INNER JOIN oportoem_datagovpt.Caucus c ON m.mpid = c.mpid WHERE f.MPID = " . $mpid . " order by MPID, FactType");
			}
		} else {
			if ($mpid == '') {
				$result = mysql_query("SELECT f.ID, f.MPID, f.FactType, f.Value, m.Name, m.DateOfBirth, m.Occupation, c.CaucusID, c.Dates FROM oportoem_datagovpt.Facts f INNER JOIN oportoem_datagovpt.MP m ON f.mpid = m.mpid INNER JOIN oportoem_datagovpt.Caucus c ON m.mpid = c.mpid WHERE c.caucusID = '" . $legislatura . "' ORDER BY f.MPID, f.FactType");			
			} else {
				$result = mysql_query("SELECT f.ID, f.MPID, f.FactType, f.Value, m.Name, m.DateOfBirth, m.Occupation, c.CaucusID, c.Dates FROM oportoem_datagovpt.Facts f INNER JOIN oportoem_datagovpt.MP m ON f.mpid = m.mpid INNER JOIN oportoem_datagovpt.Caucus c ON m.mpid = c.mpid WHERE c.caucusID = '" . $legislatura . "' AND f.MPID = " . $mpid . " ORDER BY f.MPID, f.FactType");				
			}		
		}
		break;
}		

//echo header('Content-type: text/plain');

while($row = mysql_fetch_array($result))
{
	switch ($opcao) {
		case 'MP':
			echo $row['MPID'] . "," . $row['Name'] . "," . $row['DateOfBirth'] . "," . $row['Occupation'] . "\n";
			break;
		case 'Caucus':
			echo $row['ID'] . "," . $row['MPID'] . "," . $row['CaucusID'] . "," . $row['Dates'] . "," . $row['Constituency'] . "," . $row['Party'] . "," . $row['HasActivity'] ."," . $row['HasRegistoInteresses'] ."," . $row['Name'] ."," . $row['DateOfBirth'] ."," . $row['Occupation'] ."\n";
			break;
		case 'CaucusInfo':
			echo $row['CaucusID'] . "," . $row['Dates'] . "\n";
			break;
		case 'FactsType':
			echo $row['FactType'] . "\n";
			break;
		case 'Facts':
			if ($legislatura == '') {
				echo $row['ID'] . "," . $row['MPID'] . "," . $row['FactType'] . "," . escapeCSV(removeInvalidCharacters($row['Value'])) . $row['Name'] . "," . $row['DateOfBirth'] . "," . $row['Occupation'] . "," . $row['CaucusID'] . "," . $row['Dates'] . "\n";
			} else {
				echo $row['ID'] . "," . $row['MPID'] . "," . $row['FactType'] . "," . escapeCSV(removeInvalidCharacters($row['Value'])) . ","  . $row['Name'] . "," . $row['DateOfBirth'] . "," . $row['Occupation'] . "," . $row['CaucusID'] . "," . $row['Dates'] . "\n";
			}
			break;
	}
	ob_flush(); flush();  
}

mysql_close();		

function CreateCSVLine($line) {

}

function removeInvalidCharacters($input) {

//	$value = preg_replace("/[^a-zA-Z0-9\s]/", "", $input);
	$value = $input;
	$value = str_replace(chr(10), "", $value);
	$value = str_replace(chr(13), "", $value);
	return $value;
	
}

function escapeCSV($input) {

	$value = $input;
	$value = str_replace(",", " ", $value);
	$value = str_replace("  ", " ", $value);
	return $value;

}

function logAccess() {

	$log = '';

	$log .= 'GET|';
	foreach ($_GET as $var => $value) { 
		$log .= "$var=$value;"; 
	}
	$log .= '|POST|';
	foreach ($_POST as $var => $value) { 
		$log .= "$var=$value;"; 
	}
	$log .= '|IP|';
	$log .= $_SERVER['REMOTE_ADDR'];
	$log .= '|';

	$key = $_GET['key'];
	
	$sql = sprintf("INSERT INTO oportoem_datagovpt.Log (Date, hashKey, Variables) VALUES (NOW( ), '%s', '%s')",
		mysql_real_escape_string($key),
		mysql_real_escape_string($log));
	
	mysql_query($sql) or die("Failed Query-".$sql);												
}
?>


