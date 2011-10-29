<?php
/** Deputado do Dia
 *  chamar com ?mp=id (ou aleatorio)
 *  saca as imagens do parlamento.pt, mas recomenda-se uso de imagens locais
 */
 
// Init DB:
$db = new PDO('mysql:host=127.0.0.1;port=null;dbname=transparencia',
	'transparencia', 'transparencia'); // host;port;dbname, username, password

if (isset($_REQUEST['mp']) && is_numeric($_REQUEST['mp'])) {
	$mpid = $_REQUEST['mp'];
} else {
	$mpid = (int) rand(1,4300);
}



$dados = "\n";

// Tabela MP:
$result = $db->query("SELECT Name as Nome, DateOfBirth as Nascimento, Occupation as Profissao
	FROM mp WHERE MPID=$mpid")->fetchAll(PDO::FETCH_ASSOC);
if ($result) {
	foreach ($result[0] as $k => $val) {
		$dados .= "<b>$k</b>: $val\n";
	}
	$nome = $result[0]['Nome'];
}
$dados .= "\n";

// Tabela Caucus:
$result = $db->query("SELECT Dates as Legislatura, Constituency as Distrito, Party as Partido
	FROM Caucus WHERE MPID=$mpid")->fetchAll(PDO::FETCH_ASSOC);
if ($result) {
	foreach ($result as $res) {
		foreach ($res as $k => $val) {
			$dados .=  "<b>$k</b>: $val\n";
		}
		$dados .= "\n";
	}
}

// Tabela Networks:
$result = $db->query("SELECT Cargo, Email, Wikipedia, Facebook, Twitter, Blog, Website, LinkedIn, Twitica, Radio, TV
	FROM Networks WHERE MPID=$mpid")->fetchAll(PDO::FETCH_ASSOC);
if ($result) {
	foreach ($result as $res) {
		foreach ($res as $k => $val) {
			if (!empty($val)) {
				$dados .=  "<b>$k</b>: ".makeClickableLinks($val)."\n";
			}
		}
		$dados .= "\n";
	}
}

// Tabela Facts:
$result = $db->query("SELECT FactType as Tipo, Value as Valor
	FROM Facts WHERE MPID=$mpid")->fetchAll(PDO::FETCH_ASSOC);
if ($result) {
	foreach ($result as $res) {
		$dados .= "<b>{$res['Tipo']}</b>: {$res['Valor']}\n";

	}
}



/**
 * makeClickableLinks().
 * This function converts URLs and e-mail addresses within a string into clickable hyperlinks. \n 
 * From http://stackoverflow.com/questions/980902/regex-to-turn-urls-into-links-without-messing-with-existing-links-in-the-text/987663#987663
 */ 
function makeClickableLinks($html='') {
	$strParts = preg_split( '/(<[^>]+>)/', $html, -1, PREG_SPLIT_DELIM_CAPTURE | PREG_SPLIT_NO_EMPTY );
    foreach( $strParts as $key=>$part ) {

        /*check this part isn't a tag or inside a link*/
        if( !(preg_match( '@(<[^>]+>)@', $part ) || preg_match( '@(<a[^>]+>)@', $strParts[$key - 1] )) ) {
            $strParts[$key] = preg_replace( '@((http(s)?://)?(\S+\.{1}[^\s\,\.\!]+))@', '<a href="http$3://$4">$1</a>', $strParts[$key] );
        }

    }
    $html = implode( $strParts );
	return $html;
}

?>
<html>
<head>
<title>O Deputado do Dia</title>
<style type="text/css">
<!--

html, body { margin: 0; padding: 0; width: 100%; height: 100%; }
	
body {
	background: #480;
	color: #DDD;
	font-family: Helvetica, Arial, sans-serif;
}

#content { 
	display: block;
	margin: 0 auto;
	padding-top: 100px;
	width: 960px;
	text-align: center;
}

p {
	font-size: 10px;
	letter-spacing: 0px;
	margin: 8px 0;
	text-align: center;
}

h1 {
	color: #FFF;
	letter-spacing: -2px;
	font-size: 40px;
}


a, a:link, a:visited {
	text-decoration: none;
	background: none;
	padding: 2px 3px 2px 3px;
	color: #7F4;
	-webkit-border-radius: 5px;
	-moz-border-radius: 5px;
}
a:hover {
	background: #666;
	background: rgba(0,0,0,0.4);
	color: #FFF;
}
a img.icon {
	position: relative;
	top: 2px;
}

-->
</style>
</head>
<body>
<div id="content">
	<img src="http://app.parlamento.pt/webutils/getimage.aspx?id=<?=$mpid ?>&type=deputado" />
	<h1><?=$nome ?></h1>
	<p>
		<?=nl2br($dados) ?>
	</p>
	<br/><br/>
</div>
</body>
</html>