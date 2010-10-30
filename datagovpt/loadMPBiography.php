<?php 
// http://www.oportoemconversa.com/loadMPBiography.php?start=4300&end=4310
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
	
$key = $_GET['key'] ;
if ($key == '') {
	die('invalid key');
} else {
	$hashkey = array("QQOPD4VzmHL4yhr");
	if (in_array($key, $hashkey) == false) {
		die('invalid key');
	}
}

$mpid_start = $_GET['start'] ;
$mpid_end = $mpid_start + 100; //$_GET['end'] ;


for ($mpid = $mpid_start; $mpid <= $mpid_end; $mpid++) {
	echo $mpid . '-' . date("h:i:s") .'<br>';

	$sql = "DELETE FROM oportoem_datagovpt.Facts  where mpid = " . $mpid . ";";
	mysql_query($sql) or die("Failed Query-".$sql);
	$sql = "DELETE FROM oportoem_datagovpt.Caucus  where mpid = " . $mpid . ";";
	mysql_query($sql) or die("Failed Query-".$sql);
	$sql = "DELETE FROM oportoem_datagovpt.MP where mpid = " . $mpid . ";";
	mysql_query($sql) or die("Failed Query-".$sql);
	
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
	curl_setopt($ch, CURLOPT_URL, "www.parlamento.pt/DeputadoGP/Paginas/Biografia.aspx?BID=$mpid"); 

	//return the transfer as a string 
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1); 
	curl_setopt($ch, CURLOPT_FILETIME, 1); 
	curl_setopt($ch, CURLINFO_HTTP_CODE, 1); 
	
	$html= curl_exec($ch);
	$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
	if($httpCode == 404) {
		/* Handle 404 here. */
		echo 'nao existe';			
		$sql = sprintf("INSERT INTO oportoem_datagovpt.MP (MPID, Name, DateOfBirth, CreatedOn) VALUES (%s, '%s', '%s', Now())",
				mysql_real_escape_string($mpid),
				mysql_real_escape_string('N/A'),
				mysql_real_escape_string('N/A'));			
		mysql_query($sql) or die("Failed Query-".$sql);

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
			
			$node = $xpath->evaluate("id('ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_lblErro')");		

			if ($node->length > 0) {
				$sql = sprintf("INSERT INTO oportoem_datagovpt.MP (MPID, Name, DateOfBirth, CreatedOn) VALUES (%s, '%s', '%s', Now());",
					mysql_real_escape_string($mpid),
					mysql_real_escape_string('N/A'),
					mysql_real_escape_string('N/A'));			
				mysql_query($sql) or die("Failed Query-".$sql);				
				echo 'erro<br />';
			}				
			else {
				$mp_name = '';
				$mp_dateOfBirth = '';
				$mp_occupation = '';
				
				// nome
				$node = $xpath->evaluate("id('ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_ucNome_rptContent_ctl01_lblText')");		
				if ($node->length > 0) {
					$data = $node->item(0);
					$mp_name = trim(iconv("UTF-8","ISO-8859-1",$data->nodeValue));
				}

				// datanascimento
				$node = $xpath->evaluate("id('ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_ucDOB_rptContent_ctl01_lblText')");		
				if ($node->length > 0) {
					$data = $node->item(0);
					$mp_dateOfBirth = $data->nodeValue;
				}

				// profissão
				$node = $xpath->evaluate("id('ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_ucProf_rptContent_ctl01_lblText')");		
				if ($node->length > 0) {
					$data = $node->item(0);
					$mp_occupation = trim(iconv("UTF-8","ISO-8859-1",$data->nodeValue));
				}

				$sql = sprintf("INSERT INTO oportoem_datagovpt.MP (MPID, Name, DateOfBirth, Occupation, CreatedOn) VALUES (%s, '%s', '%s', '%s', Now());",
					mysql_real_escape_string($mpid),
					mysql_real_escape_string($mp_name),
					mysql_real_escape_string($mp_dateOfBirth),
					mysql_real_escape_string($mp_occupation));			

				mysql_query($sql) or die("Failed Query-".$sql);	
				
				if ($mp_name = '') {
					echo 'nome vazio';
				}
				
				// legislaturas
				$node = $xpath->evaluate("id('ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_gvTabLegs')/tr");
				// primeiro linha é o titulo da tabela
				for ($i = 1; $i < $node->length; $i++) {
					//$a = $xpath->evaluate("id('ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_gvTabLegs')/tr");
					$caucus_dates = '';
					$caucus_constituency = '';
					$caucus_party = '';
					$caucus_hasActivities = '';
					$caucus_hasRegistoInteresses = '';
					
					$linha = $node->item($i);
					
					$caucus_dates = trim(iconv("UTF-8","ISO-8859-1",$linha->childNodes->item(0)->nodeValue));
					$caucus_constituency = trim(iconv("UTF-8","ISO-8859-1",$linha->childNodes->item(3)->nodeValue));
					$caucus_party = trim(iconv("UTF-8","ISO-8859-1",$linha->childNodes->item(4)->nodeValue));
					
					if ($linha->childNodes->item(1)->nodeValue != "") {
						$caucus_hasActivities = 'true';
					} else {
						$caucus_hasActivities = 'false';
					}
					
					if ($linha->childNodes->item(2)->nodeValue != "") {
						$caucus_hasRegistoInteresses = 'true';
					} else {
						$caucus_hasRegistoInteresses = 'false';
					}
					
					$sql = sprintf("INSERT INTO oportoem_datagovpt.Caucus (MPID, Dates, Constituency, Party, HasActivity, HasRegistoInteresses, CreatedOn) VALUES (%s, '%s', '%s', '%s', %s, %s, Now())",
						mysql_real_escape_string($mpid),
						mysql_real_escape_string($caucus_dates),
						mysql_real_escape_string($caucus_constituency),
						mysql_real_escape_string($caucus_party),
						mysql_real_escape_string($caucus_hasActivities),
						mysql_real_escape_string($caucus_hasRegistoInteresses));			
					
					mysql_query($sql) or die("Failed Query-".$sql);				
					
				} // fim legislaturas		
				
				// Cargos que desempenha
				$node = $xpath->evaluate("id('ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_pnlCargosDesempenha')/table/tr");
				// primeiro linha é o titulo da tabela
				for ($i = 1; $i < $node->length; $i++) {
					$linha = $node->item($i);
					$cargo = trim(iconv("UTF-8","ISO-8859-1",$linha->childNodes->item(2)->nodeValue));

					$sql = sprintf("INSERT INTO oportoem_datagovpt.Facts (MPID, FactType, Value, CreatedOn) VALUES (%s, 'CargosDesempenha', '%s', now())",
						mysql_real_escape_string($mpid),
						mysql_real_escape_string($cargo));						

					mysql_query($sql) or die("Failed Query-".$sql);										
				}				
				
				// Cargos que desempenhou
				$node = $xpath->evaluate("id('ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_pnlCargosExercidos')/table/tr");
				// primeiro linha é o titulo da tabela
				for ($i = 1; $i < $node->length; $i++) {
					$linha = $node->item($i);
					$cargo = trim(iconv("UTF-8","ISO-8859-1",$linha->childNodes->item(2)->nodeValue));

					$sql = sprintf("INSERT INTO oportoem_datagovpt.Facts (MPID, FactType, Value, CreatedOn) VALUES (%s, 'CargosExercidos', '%s', now())",
						mysql_real_escape_string($mpid),
						mysql_real_escape_string($cargo));						

					mysql_query($sql) or die("Failed Query-".$sql);										
				}

				//Comissões Parlamentares
				$node = $xpath->evaluate("id('ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_pnlComissoes')/table/tr");
				// primeiro linha é o titulo da tabela
				for ($i = 1; $i < $node->length; $i++) {
					$linha = $node->item($i);
					$name = trim(iconv("UTF-8","ISO-8859-1",$linha->childNodes->item(2)->nodeValue));

					$sql = sprintf("INSERT INTO oportoem_datagovpt.Facts (MPID, FactType, Value, CreatedOn) VALUES (%s, 'Comissoes', '%s', Now())",
						mysql_real_escape_string($mpid),
						mysql_real_escape_string($name));						

					mysql_query($sql) or die("Failed Query-".$sql);										
				}				

				//Hailitações Literárias
				$node = $xpath->evaluate("id('ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_pnlHabilitacoes')/table/tr");
				// primeiro linha é o titulo da tabela
				for ($i = 1; $i < $node->length; $i++) {
					$linha = $node->item($i);
					$qualification = trim(iconv("UTF-8","ISO-8859-1",$linha->childNodes->item(2)->nodeValue));

					$sql = sprintf("INSERT INTO oportoem_datagovpt.Facts (MPID, FactType, Value, CreatedOn) VALUES (%s, 'HabilitacoesLiterarias', '%s', Now())",
						mysql_real_escape_string($mpid),
						mysql_real_escape_string($qualification));

					mysql_query($sql) or die("Failed Query-".$sql);										
				}				
				
				//Condecoracoes
				$node = $xpath->evaluate("id('ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_pnlCondecoracoes')/table/tr");
				// primeiro linha é o titulo da tabela
				for ($i = 1; $i < $node->length; $i++) {
					$linha = $node->item($i);
					$factValue = trim(iconv("UTF-8","ISO-8859-1",$linha->childNodes->item(2)->nodeValue));

					$sql = sprintf("INSERT INTO oportoem_datagovpt.Facts (MPID, FactType, Value, CreatedOn) VALUES (%s, 'Condecoracoes', '%s', Now())",
						mysql_real_escape_string($mpid),
						mysql_real_escape_string($factValue));

					mysql_query($sql) or die("Failed Query-".$sql);										
				}				
					
				}
			} // fim deputado
	}
	
	ob_flush(); flush(); 
	if ($mpid % 50 == 50) {
		sleep(5);
	}
	else {
		sleep(0.1);	
	}

}		
	
// update caucusid
$sql = "UPDATE oportoem_datagovpt.Caucus set caucusid = rtrim(ltrim(substring(dates, 1, locate(' ', dates)))) where caucusid is null";
mysql_query($sql) or die("Failed Query-".$sql);			
	
mysql_close();		
?>