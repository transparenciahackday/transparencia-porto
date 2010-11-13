<?php

/** Teste reverse-engineering hash dos URLs dos PDFs no site da AR
 */
$hashOrig ="6148523063446f764c324679626d56304c334e706447567a4c31684a544556484c305242556b6b76524546535355467963585670646d38764d734b714a5449775532567a63384f6a627955794d45786c5a326c7a6247463061585a684c3052425569314a4c5441794d5335775a47593d";

echo base64_decode(hexToStr($hashOrig)); // BINGO!


function hexToStr($hex)
{
    $string='';
    for ($i=0; $i < strlen($hex)-1; $i+=2)
    {
        $string .= chr(hexdec($hex[$i].$hex[$i+1]));
    }
    return $string;
}

?>