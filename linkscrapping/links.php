<html><head><title>AR PDFs</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
</head><body>
<?php

/** Gera Links para PDFs da Assembleia
 *  Assegurar que o encoding do ficheiro é UTF-8!!!
 */
 
 
// Define PDFs:
// caminho -> base do nome do ficheiro -> num. de PDFs (por sessao legislativa)
$sacar = array(
	"http://arnet/sites/VIILEG/DARI/DARIArquivo/%d.ª Sessão Legislativa" =>
		array('DAR' => 
			array(109, 112, 89, 108)),
	"http://arnet/sites/VIIILEG/DARI/DARIArquivo/%d.ª Sessão Legislativa" =>
		array('DARI' 
			=> array(91, 107, 33)),
	"http://arnet/sites/IXLEG/DARI/DARIArquivo/%d.ª Sessão Legislativa" =>
		array('DARI' 
			=> array(146, 108, 24)),
	"http://arnet/sites/XLEG/DARI/DARIArquivo/%dª Sessão Legislativa" =>
		array('DARI' 
			=> array(149, 110, 111, 106)),
	"http://arnet/sites/XILEG/DARI/DARIArquivo/%dª Sessão Legislativa" =>
		array('DAR-I-' 
			=> array(84, 30)) 
		// o ultimo numero diz respeito à actual legislatura, logo em actualização
);


// Percorrer o array
foreach ($sacar as $caminho => $ficheiros) {
	foreach ($ficheiros as $template => $quantos) {
		$s = 0;
		foreach ($quantos as $num) {
			$s++;
			$path = sprintf($caminho, $s);
			
			echo "<p>$path</p><code>"; // html?

			for ($i=1;$i<=$num;$i++) {
				$ni = str_pad($i, 3, "0", STR_PAD_LEFT);

				$nome = $template.$ni.'.pdf';
				$query = http_build_query(array(
						'doc'	=> strToHex(base64_encode($path."/$nome")),
						'nome'	=> $nome
					), '', '&');
					
				$url = 'http://app.parlamento.pt/darpages/dardoc.aspx?'.$query;
				
				//------------------------------------------------------------------
				// em vez de fazer links podemos fazer qualquer coisa com estas URLs
				//
				echo '<a href="'.$url.'">'.$ni.'</a>  ';
				//------------------------------------------------------------------

			}
			
			echo "</code>"; // html?
			
		}
	}
}



//-----------------------------------------
// FUNCTIONS
//-----------------------------------------

function strToHex($string) {
    $hex='';
    for ($i=0; $i < strlen($string); $i++)     {
        $hex .= dechex(ord($string[$i]));
    }
    return $hex;
}


?>
</body></html>