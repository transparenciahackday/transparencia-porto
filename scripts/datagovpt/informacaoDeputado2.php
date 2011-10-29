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
$output = $_GET['output'] ;

if ($output == '') $output = 'atom';

if ($opcao == '') die('opção inválida');
switch ($opcao) {
	case 'MP':
		if ($legislatura == '') {
			if ($mpid == '') {
				$result = mysql_query("SELECT m.MPID, m.Name, m.DateOfBirth, m.Occupation FROM oportoem_datagovpt.MP m order by m.MPID");			
			} else {
				$result = mysql_query("SELECT m.MPID, m.Name, m.DateOfBirth, m.Occupation FROM oportoem_datagovpt.MP m WHERE m.MPID = ". $mpid ." order by m.MPID");			
			}
		} else {
			if ($mpid == '') {
				$result = mysql_query("SELECT m.MPID, m.Name, m.DateOfBirth, m.Occupation FROM oportoem_datagovpt.MP as m INNER JOIN oportoem_datagovpt.Caucus as c ON m.mpid = c.mpid WHERE c.caucusid =  '" . $legislatura . "' ORDER BY MPID");
			} else {
				$result = mysql_query("SELECT m.MPID, m.Name, m.DateOfBirth, m.Occupation FROM oportoem_datagovpt.MP as m INNER JOIN oportoem_datagovpt.Caucus as c ON m.mpid = c.mpid WHERE m.mpid = " . $mpid . " c.caucusid =  '" . $legislatura . "' ORDER BY MPID");			
			}
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
				$result = mysql_query("SELECT f.ID, f.MPID, f.FactType, f.Value, m.Name, m.DateOfBirth, m.Occupation, c.CaucusID, c.Dates FROM  oportoem_datagovpt.Facts f  INNER JOIN oportoem_datagovpt.MP m ON f.mpid = m.mpid INNER JOIN oportoem_datagovpt.Caucus c ON m.mpid = c.mpid order by MPID, FactType");
			} else {
				$result = mysql_query("SELECT f.ID, f.MPID, f.FactType, f.Value, m.Name, m.DateOfBirth, m.Occupation, c.CaucusID, c.Dates FROM  oportoem_datagovpt.Facts f  INNER JOIN oportoem_datagovpt.MP m ON f.mpid = m.mpid INNER JOIN oportoem_datagovpt.Caucus c ON m.mpid = c.mpid WHERE f.MPID = " . $mpid . " order by MPID, FactType");
			}
		} else {
			if ($mpid == '') {
				$result = mysql_query("SELECT f.ID, f.MPID, f.FactType, f.Value, m.Name, m.DateOfBirth, m.Occupation, c.CaucusID, c.Dates FROM oportoem_datagovpt.Facts f INNER JOIN oportoem_datagovpt.MP m ON f.mpid = m.mpid INNER JOIN oportoem_datagovpt.Caucus c ON m.mpid = c.mpid WHERE c.caucusID = '" . $legislatura . "' ORDER BY f.MPID, f.FactType");			
			} else {
				$result = mysql_query("SELECT f.ID, f.MPID, f.FactType, f.Value, m.Name, m.DateOfBirth, m.Occupation, c.CaucusID, c.Dates FROM oportoem_datagovpt.Facts f INNER JOIN oportoem_datagovpt.MP m ON f.mpid = m.mpid INNER JOIN oportoem_datagovpt.Caucus c ON m.mpid = c.mpid WHERE c.caucusID = '" . $legislatura . "' AND f.MPID = " . $mpid . " ORDER BY f.MPID, f.FactType");				
			}		
		}
		break;
	default:
		die('no one here by that name...');
}		

//echo header('Content-type: text/plain');
echo CreateHeader($output);

$i = 0;
while($row = mysql_fetch_array($result))
{
	switch ($opcao) {
		case 'MP':
			$arr = array("MPID" => $row['MPID'], "Name" => $row['Name'], "DateOfBirth" => $row['DateOfBirth'], "Occupation" => $row['Occupation']);
			echo CreateLine($arr, $output, $i);
			break;
		case 'Caucus':
			$arr = array("ID" => $row['ID'], "MPID" => $row['MPID'], "CaucusID" => $row['CaucusID'], "Dates" => $row['Dates'], "Constituency" => $row['Constituency'], "Party" => $row['Party'], "HasActivity" => $row['HasActivity'], "HasRegistoInteresses" => $row['HasRegistoInteresses'], "Name" => $row['Name'], "DateOfBirth" => $row['DateOfBirth'], "Occupation" => $row['Occupation']);
			echo CreateLine($arr, $output, $i);
			break;
		case 'CaucusInfo':
			$arr = array("CaucusID" => $row['CaucusID'], "Dates" => $row['Dates']);
			echo CreateLine($arr, $output, $i);
			break;
		case 'FactsType':
			$arr = array("FactType" => $row['FactType']);
			echo CreateLine($arr, $output, $i);
			break;
		case 'Facts':
			$arr = array("ID" => $row['ID'], 
			             "MPID" => $row['MPID'], 
						 "FactType" => $row['FactType'], 
						 "Value" => $row['Value'], 
						 "Name" => $row['Name'], 
						 "DateOfBirth" => $row['DateOfBirth'], 
						 "Occupation" => $row['Occupation'], 
						 "CaucusID" => $row['CaucusID'], 
						 "Dates" => $row['Dates']);
			echo CreateLine($arr, $output, $i);
		break;
	}
	ob_flush(); flush();  
	$i++;
}

echo CreateFooter($output);

mysql_close();		

function CreateHeader($output) {

	switch ($output) {
		case 'csv':
			$resultado = '';
			break;
		case 'atom':
			$resultado = '<?xml version="1.0" encoding="UTF-8"?>';
			$resultado .= '<feed xmlns="http://www.w3.org/2005/Atom">';
			$resultado .= '<id>http://www.oportoemconversa.com/datagovpt/informacaoDeputado.php</id>';
			$resultado .= '<title type="text">Informacao Deputado</title>';
			$resultado .= '<link href="www.oportoemconversa.com/datagovpt/informacaoDeputado.php" type="application/atom+xml"></link>';
			$resultado .= '<updated>2008-05-20T14:50:15.806Z</updated>';
			$resultado .= '<subtitle type="text">infodeputado</subtitle>';
			$resultado .= '<generator>hackday_transparencia</generator>';
			break;
		case 'atom-html':
			$resultado = '<?xml version="1.0" encoding="UTF-8"?>';
			$resultado .= '<feed xmlns="http://www.w3.org/2005/Atom">';
			$resultado .= '<id>http://www.oportoemconversa.com/datagovpt/informacaoDeputado.php</id>';
			$resultado .= '<title type="text">Informacao Deputado</title>';
			$resultado .= '<link href="www.oportoemconversa.com/datagovpt/informacaoDeputado.php" type="application/atom+xml"></link>';
			$resultado .= '<updated>2008-05-20T14:50:15.806Z</updated>';
			$resultado .= '<subtitle type="text">infodeputado</subtitle>';
			$resultado .= '<generator>hackday_transparencia</generator>';
			break;
	}
	
	return $resultado;

}

function CreateFooter($output) {

	$resultado = '';
	switch ($output) {
		case 'csv':
			$resultado = '';
			break;
		case 'atom':
			$resultado = '</feed>';
			break;	
		case 'atom-html':
			$resultado = '</feed>';
			break;	
	}
	return $resultado;
}

function CreateLine($line, $output, $i) {	

	$resultado = '';
	switch ($output) {
		case 'atom':
			$resultado = CreateAtomRow($line, $i);
			break;
		case 'csv':
			$resultado = CreateCSVLine($line);
			break;				
		case 'atom-html':
			$resultado = CreateAtomHTMLLine($line);
			break;	
	}
	return $resultado;
}

function CreateCSVLine($line) {	

	$resultado = '';
	while (list($key, $val) = each($line)) {
		$resultado .= escapeCSV(removeInvalidCharacters($val)) . ',';
	}
	$resultado = substr($resultado, 0, strlen($resultado)-1) . "\n";
	return $resultado;
	
}

function CreateAtomRow($line, $i) {	

	$resultado = '';
	
	$itemBase = '';
	$itemBase .= '<entry xmlns="http://www.w3.org/2005/Atom">';
	$itemBase .= '  <title type="text">deputado1</title>';
	$itemBase .= '  <id>http://www.oportoemconversa.com/datagovpt/' . $i. '</id>';
	$itemBase .= '  <updated>' . date('c') . '</updated>';
	$itemBase .= '  <author>';
	$itemBase .= '    <name>joeuser</name>';
	$itemBase .= '  </author>';
	$itemBase .= '  <summary type="text">Atom Feed entry 1</summary>';
	$itemBase .= '  <content type="application/xml">';
		
	while (list($key, $val) = each($line)) {
		$resultado .= '<' . $key . '>' . htmlentities(str_replace(chr(160), "", $val)) . '</' . $key . '>';
	}
	$resultado = '<row>' . $resultado . '</row>';

	$resultado1 = $itemBase . $resultado;
	
	$resultado1 .= '  </content>';
	$resultado1 .=  '</entry>';
	
	return $resultado1;
}

function CreateAtomHTMLLine($line) {

	$resultado = '';
	
	$itemBase = '';
	$itemBase .= '<entry xmlns="http://www.w3.org/2005/Atom">';
	$itemBase .= '  <title type="text">deputado1</title>';
	$itemBase .= '  <id>http://www.oportoemconversa.com/datagovpt/' . $i. '</id>';
	$itemBase .= '  <updated>' . date('c') . '</updated>';
	$itemBase .= '  <author>';
	$itemBase .= '    <name>joeuser</name>';
	$itemBase .= '  </author>';
	//$itemBase .= '  <summary type="text">';
	$itemBase .= '  <content>';

	while (list($key, $val) = each($line)) {
		$itemBase .= escapeCSV(removeInvalidCharacters($val)) . ',';
	}
	
	$itemBase .= '  </content>';
	//$itemBase .= '  <content type="application/xml">';
	//$itemBase .= '  <content>';

	//while (list($key, $val) = each($line)) {
//		$resultado .= escapeCSV(removeInvalidCharacters($val)) . ',';
	//}
	
	
//	while (list($key, $val) = each($line)) {
//		$resultado .= '<td>' . htmlentities(str_replace(chr(160), "", $val)) . '</td>';
//	}
//	$resultado = '<table><tr>' . $resultado . '</tr></table>';

	$resultado1 = $itemBase . $resultado;
	
	$resultado1 .=  '</entry>';
	
	return $resultado1;
	
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


