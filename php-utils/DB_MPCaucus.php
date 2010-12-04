<?php
/** MP+Caucus
 *  chamar com ?csv para obter download
 *  chamar com ?todos para obter todos os registos (default = 50)
 */
 
// Init DB:
$db = new PDO('mysql:host=127.0.0.1;port=null;dbname=transparencia',
	'transparencia', 'transparencia'); // host;port;dbname, username, password

// parametros:
if (isset($_REQUEST['csv'])) {
	header("Content-type: application/csv"); // download CSV
	header("Content-Disposition: attachment; filename=\"MPCaucus.csv\"");
} else {
	echo "<pre>"; // ver preformatado no browser
}
$limit = 'LIMIT 0,50';
if (isset($_REQUEST['todos'])) {
	$limit = '';
}



// Tabela MP:
$result = $db->query("SELECT DISTINCT MPID, Name as Nome, DateOfBirth as Nascimento, Occupation as Profissao
	FROM mp {$limit}")->fetchAll(PDO::FETCH_ASSOC);
if ($result) {
	$mpChaves = array_keys($result[0]); // chaves (para 1a linha do CSV)
	$dados = $result;
	
	foreach ($dados as &$mpLinha) {
		
		// Tabela Caucus:
		$result = $db->query("SELECT CaucusID as Legislatura, Dates as Datas, Constituency as Distrito, Party as Partido 
			FROM caucus WHERE MPID={$mpLinha['MPID']}")->fetchAll(PDO::FETCH_ASSOC);
		if ($result) {
			$cChaves = array_keys($result[0]);  // chaves (para 1a linha do CSV)
			
			foreach($cChaves as $k) {
				$a = array(); // array associativo para multiplos valores/atributo
				foreach($result as $cLinha) {
					$a[] = $cLinha[$k];
				}
				$mpLinha[$k] = implode('|', $a); // multivalor separados por pipes
			}

		}
	}
}

// OUTPUT
array_unshift($dados, array_merge($mpChaves, $cChaves)); // merge da 1a linha (atributos)
outputCSV($dados);


/* Array bidimensional -> CSV 
 * De algures na net
 */
function outputCSV($data) {
    $outstream = fopen("php://output", 'w');
    function __outputCSV(&$vals, $key, $filehandler) {
        fputcsv($filehandler, $vals, ';', '"');
    }
    array_walk($data, '__outputCSV', $outstream);
    fclose($outstream);
}

?>