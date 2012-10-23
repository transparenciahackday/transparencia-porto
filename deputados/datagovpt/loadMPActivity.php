<?php 
// http://www.oportoemconversa.com/curl2.php?start=4300&end=4310
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

// todos os deputados  em todas as legislaturas
$mpid_start = 2167; //$_GET['start'] ;
$mpid_end = 2168; //$_GET['end'] ;

$caucusid_start = 1; //$_GET['start'] ;
$caucusid_end = 2; //$_GET['end'] ;

$sql = "DELETE FROM oportoem_datagovpt.Activities"; // where id >= " . $mpid_start;
mysql_query($sql) or die("Failed Query-".$sql);

for ($caucusid = $caucusid_start; $caucusid < $caucusid_end; $caucusid++) { //legislaturas
	for ($mpid = $mpid_start; $mpid < $mpid_end; $mpid++) { // deputados
	
		echo $mpid . '-' . date("h:i:s") .'<br>';
		
		$realCaucusId = 'X';
		
		// create curl resource 
		$ch = curl_init(); 

		$header[0] = "Accept: text/xml,application/xml,application/xhtml+xml,"; 
		$header[0] .= "text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5"; 
		$header[] = "Cache-Control: max-age=0"; 
		$header[] = "Connection: keep-alive"; 
		$header[] = "Keep-Alive: 115"; 
		$header[] = "ISO-8859-1,utf-8;q=0.7,*;q=0.7"; 
		$header[] = "Accept-Language: en-us,en;q=0.5"; 
		$header[] = "Pragma: "; // browsers keep this blank	

		curl_setopt($ch, CURLOPT_USERAGENT, 'Googlebot/2.1 (+http://www.google.com/bot.html)'); 
		curl_setopt($ch, CURLOPT_HTTPHEADER, $header); 
		curl_setopt($ch, CURLOPT_ENCODING, 'gzip,deflate'); 
		curl_setopt($ch, CURLOPT_AUTOREFERER, true); 
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1); 
		curl_setopt($ch, CURLOPT_TIMEOUT, 100); 
	  
		// set url 
		curl_setopt($ch, CURLOPT_URL, "www.parlamento.pt/DeputadoGP/Paginas/ActividadeDeputado.aspx?BID=$mpid&lg=$realCaucusId"); 

		//return the transfer as a string 
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1); 
		curl_setopt($ch, CURLOPT_FILETIME, 1); 
		curl_setopt($ch, CURLINFO_HTTP_CODE, 1); 
		
		$html= curl_exec($ch);
		$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
		if($httpCode == 404) {
			/* Handle 404 here. */
			echo 'nao existe';			
		}
		else {		
		
			if (!$html) {
				echo "ERROR NUMBER: ".curl_errno($ch);
				echo "ERROR: ".curl_error($ch);
			}		
			else {
			
				// close curl resource to free up system resources 
				curl_close($ch);      
				
				$dom = new DOMDocument();
				@$dom->loadHTML($html);
				
				$xpath = new DOMXPath($dom);
		
				$node = $xpath->evaluate("id('ctl00_ctl13_g_5a179f40_fba7_4f68_8ee4_687b11022fe3_ctl00_lblNoResults')");		
				
				if ($node->nodeValue != '') {
				echo 'não existe';				
					mysql_query($sql) or die("Failed Query-".$sql);				
				}				
				else {
				
					// iniciativas apresentaas
					$node = $xpath->evaluate("id('ctl00_ctl13_g_5a179f40_fba7_4f68_8ee4_687b11022fe3_ctl00_ActividadeDeputado_Legislatura1_dtgIniciativas')/tr");
					
					// primeiro linha é o titulo da tabela
					for ($i = 1; $i < $node->length; $i++) {
						$linha = $node->item($i);
						$tipo2 = trim(iconv("UTF-8","ISO-8859-1",$linha->childNodes->item(0)->nodeValue));
						$numero = trim(iconv("UTF-8","ISO-8859-1",$linha->childNodes->item(1)->nodeValue));
						$sessao = trim(iconv("UTF-8","ISO-8859-1",$linha->childNodes->item(2)->nodeValue));
						$titulo = trim(iconv("UTF-8","ISO-8859-1",$linha->childNodes->item(3)->nodeValue));
						
						$sql = sprintf("INSERT INTO oportoem_datagovpt.Activities (MPID, CaucusId, tipo1, tipo2, numero, sessao, titulo, CreatedOn) VALUES (%s, %s, 'IniciativaApresentada', '%s', '%s', '%s', '%s', now())",
							mysql_real_escape_string($mpid),
							mysql_real_escape_string($caucusid),
							mysql_real_escape_string($tipo2),
							mysql_real_escape_string($numero),
							mysql_real_escape_string($sessao),
							mysql_real_escape_string($titulo));						

						echo 'activitiesok<br/>';
						mysql_query($sql) or die("Failed Query-".$sql);										
					}		
					
					// comissoes
					$node = $xpath->evaluate("id('ctl00_ctl13_g_5a179f40_fba7_4f68_8ee4_687b11022fe3_ctl00_ActividadeDeputado_Legislatura1_dtgIntervencoes')/tr");
					
					// primeiro linha é o titulo da tabela
					for ($i = 1; $i < $node->length; $i++) {
						$linha = $node->item($i);
						$sessao = trim(iconv("UTF-8","ISO-8859-1",$linha->childNodes->item(2)->nodeValue));
						$titulo = trim(iconv("UTF-8","ISO-8859-1",$linha->childNodes->item(3)->nodeValue));						
						$tipo2 = trim(iconv("UTF-8","ISO-8859-1",$linha->childNodes->item(4)->nodeValue));
						
						$sql = sprintf("INSERT INTO oportoem_datagovpt.Activities (MPID, CaucusId, tipo1, tipo2, sessao, titulo, CreatedOn) VALUES (%s, %s, 'Intervencoes', '%s', '%s', '%s', now())",
							mysql_real_escape_string($mpid),
							mysql_real_escape_string($caucusid),
							mysql_real_escape_string($tipo2),
							mysql_real_escape_string($sessao),
							mysql_real_escape_string($titulo));						

						echo 'intervencoesok<br/>';
						echo $sql;
						mysql_query($sql) or die("Failed Query-".$sql);										
					}
					
					
					
				
				}
			}
		}
	ob_flush(); flush(); sleep(0.1);
		
	}
}	

mysql_close();		
?>