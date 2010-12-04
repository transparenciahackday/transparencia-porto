<pre>
<?php
/** Sexos
 */
 
// Init DB:
$db = new PDO('mysql:host=127.0.0.1;port=null;dbname=transparencia',
	'transparencia', 'transparencia'); // host;port;dbname, username, password
 
$legislaturas = array('I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI');
 
$where = '';


if($femininos = file('nomesF.txt')) {
	foreach ($femininos as &$n) {
		$n = trim($n);
	}
	
	foreach ($legislaturas as $legislatura) {
	
		$where = "LEFT JOIN caucus ON mp.MPID=caucus.MPID WHERE caucusID='{$legislatura}'";
		
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
		
		echo "$legislatura Legislatura\n-----------------------\n";
		echo "Total: {$total} \n";
		echo "Homens: ".($total-$sexoF)." (".round((($total-$sexoF)/$total)*100)."%)\n";
		echo "Mulheres: {$sexoF} (".round(($sexoF/$total)*100)."%) \n\n";
		
	}
}

?>
</pre>