<pre>
<?php
/** MP+Caucus
 *  chamar com ?mp=id
 */
 
// Init DB:
$db = new PDO('mysql:host=127.0.0.1;port=null;dbname=transparencia',
	'transparencia', 'transparencia'); // host;port;dbname, username, password

$mpid = (int) rand(1,4300);
if (isset($_REQUEST['mp']) && is_numeric($_REQUEST['mp'])) {
	$mpid = $_REQUEST['mp'];
}

echo '<img src="imgs/'.$mpid.'.jpg" align="right" />';
// Tabela MP:
$result = $db->query("SELECT Name as Nome, DateOfBirth as Nascimento, Occupation as Profissao
	FROM mp WHERE MPID=$mpid")->fetchAll(PDO::FETCH_ASSOC);
if ($result) {
	foreach ($result[0] as $k => $val) {
		echo "<b>$k</b>: $val\n";
	}
}
echo "---------------------------------------------\n";

// Tabela Caucus:
$result = $db->query("SELECT Dates as Legislatura, Constituency as Distrito, Party as Partido
	FROM Caucus WHERE MPID=$mpid")->fetchAll(PDO::FETCH_ASSOC);
if ($result) {
	foreach ($result as $res) {
		foreach ($res as $k => $val) {
			echo "<b>$k</b>: $val\n";
		}
		echo "---------------------------------------------\n";
	}
}

// Tabela Networks:
$result = $db->query("SELECT Cargo, Email, Wikipedia, Facebook, Twitter, Blog, Website, LinkedIn, Twitica, Radio, TV
	FROM Networks WHERE MPID=$mpid")->fetchAll(PDO::FETCH_ASSOC);
if ($result) {
	foreach ($result as $res) {
		foreach ($res as $k => $val) {
			if (!empty($val)) {
				echo "<b>$k</b>: ".makeClickableLinks($val)."\n";
			}
		}
		echo "---------------------------------------------\n";
	}
}

// Tabela Facts:
$result = $db->query("SELECT FactType as Tipo, Value as Valor
	FROM Facts WHERE MPID=$mpid")->fetchAll(PDO::FETCH_ASSOC);
if ($result) {
	foreach ($result as $res) {
		echo "<b>{$res['Tipo']}</b>: {$res['Valor']}\n";
		echo "---------------------------------------------\n";
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
</pre>