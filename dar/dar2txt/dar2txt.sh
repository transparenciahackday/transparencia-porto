#!/bin/sh

FILENAME=$1

python pdf2xml.py -t xml ${FILENAME} > ${FILENAME/%pdf/xml}
python xml2txt.py ${FILENAME/%pdf/xml} ${FILENAME/%pdf/txt}

