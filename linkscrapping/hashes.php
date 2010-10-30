<?php

/** Teste reverse-engineering hash dos URLs dos PDFs no site da AR
 */
$hashOrig ="6148523063446f764c324679626d56304c334e706447567a4c306c59544556484c305242556b6b76524546535355467963585670646d38764d793743716955794d464e6c633350446f32386c4d6a424d5a5764706332786864476c325953394551564a4a4d4445344c6e426b5a673d3d";

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