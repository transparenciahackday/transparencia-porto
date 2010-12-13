<?php
/** Sexos
 */
 
$where = '';
//$where = "LEFT JOIN caucus ON mp.MPID=caucus.MPID WHERE caucusID='X'";
 
// Init DB:
$db = new PDO('mysql:host=127.0.0.1;port=null;dbname=transparencia',
	'transparencia', 'transparencia'); // host;port;dbname, username, password

if($femininos = file('nomesF.txt')) {
	foreach ($femininos as &$n) {
		$n = trim($n);
	}
	
	// Tabela MP:
	$result = $db->query("SELECT DISTINCT mp.MPID, mp.Name FROM mp {$where}"
		)->fetchAll(PDO::FETCH_ASSOC);
	if ($result) {
		$total = 0;
		$sexoF = 0;
		foreach ($result as $deputado) {
			$total++;
			$nomes = array();
			$nomes = explode(' ', $deputado['Name']);
			if (in_array($nomes[0], $femininos)) { $sexoF++; }
		}
	}
	
	echo "Total: {$total} \n";
	echo "Homens: ".($total-$sexoF)." (".round((($total-$sexoF)/$total)*100)."%)\n";
	echo "Mulheres: {$sexoF} (".round(($sexoF/$total)*100)."%) \n\n";
}



?>