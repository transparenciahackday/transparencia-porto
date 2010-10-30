<html><head><title>AR PDFs</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1"/>
</head><body>
<?php

$sacar = array(
	'DAR-I-' => array (
		"http://arnet/sites/XILEG/DARI/DARIArquivo/2ª Sessão Legislativa" => 30,
		"http://arnet/sites/XILEG/DARI/DARIArquivo/1ª Sessão Legislativa" => 84,
	),
	'DARI' => array(
		"http://arnet/sites/XLEG/DARI/DARIArquivo/4ª Sessão Legislativa" => 106,
		"http://arnet/sites/XLEG/DARI/DARIArquivo/3ª Sessão Legislativa" => 111,
		"http://arnet/sites/XLEG/DARI/DARIArquivo/2ª Sessão Legislativa" => 110,
		"http://arnet/sites/XLEG/DARI/DARIArquivo/1ª Sessão Legislativa" => 149,
		
		"http://arnet/sites/IXLEG/DARI/DARIArquivo/3.ª Sessão Legislativa" => 24,
		"http://arnet/sites/IXLEG/DARI/DARIArquivo/2.ª Sessão Legislativa" => 108,
		"http://arnet/sites/IXLEG/DARI/DARIArquivo/1.ª Sessão Legislativa" => 146,
		
		"http://arnet/sites/VIIILEG/DARI/DARIArquivo/3.ª Sessão Legislativa" => 33,
		"http://arnet/sites/VIIILEG/DARI/DARIArquivo/2.ª Sessão Legislativa" => 107,
		"http://arnet/sites/VIIILEG/DARI/DARIArquivo/1.ª Sessão Legislativa" => 91,
	),
	'DAR' => array(		
		"http://arnet/sites/VIILEG/DARI/DARIArquivo/4.ª Sessão Legislativa" => 108,
		"http://arnet/sites/VIILEG/DARI/DARIArquivo/3.ª Sessão Legislativa" => 89,
		"http://arnet/sites/VIILEG/DARI/DARIArquivo/2.ª Sessão Legislativa" => 112,
		"http://arnet/sites/VIILEG/DARI/DARIArquivo/1.ª Sessão Legislativa" => 109,
	)
);

foreach ($sacar as $formato => $localPaths) {
	foreach ($localPaths as $localPath => $num) {
		echo "<h3>$localPath</h3><p>";

		for ($i=1;$i<=$num;$i++) {
			$ni = str_pad($i, 3, "0", STR_PAD_LEFT);

			$nome = $formato.$ni.'.pdf';
			$query = http_build_query(array(
					'doc'	=> strToHex(base64_encode($localPath."/$nome")),
					'nome'	=> $nome
				), '', '&');
				
			$url = 'http://app.parlamento.pt/darpages/dardoc.aspx?'.$query;

			echo '<a href="'.$url.'">'.$nome.'</a> | ';

		}

		echo "</p>";
	}
}
// FUNCTIONS

function strToHex($string)
{
    $hex='';
    for ($i=0; $i < strlen($string); $i++)
    {
        $hex .= dechex(ord($string[$i]));
    }
    return $hex;
}


?>
</body></html>