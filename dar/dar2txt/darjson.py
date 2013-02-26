#!/usr/bin/env python
# -*- coding: utf-8 -*-

TMP_DIR = "./temp"

import sys, os, shutil

def pdf2xml(filename):
    outfilename = os.path.join(TMP_DIR, os.path.basename(filename).replace('.pdf', '.xml'))
    os.system("python pdf2xml.py -o %s %s" % (outfilename, filename))
    return outfilename

def xml2pretxt(filename):
    outfilename = os.path.join(TMP_DIR, os.path.basename(filename).replace('.xml', '.pre.txt'))
    os.system("python xml2txt.py %s %s" % (filename, outfilename))
    return outfilename

def pretxt2txt(filename):
    outfilename = os.path.join(TMP_DIR, os.path.basename(filename).replace('.pre.txt', '.txt'))
    os.system("python txtpostproc.py %s %s" % (filename, outfilename))
    return outfilename

def txt2json(filename):
    outfilename = os.path.join(TMP_DIR, os.path.basename(filename).replace('.txt', '.json'))
    os.system("python txt2json.py %s %s" % (filename, outfilename))
    return outfilename

if __name__ == "__main__":
    # TODO: Argparse
    # -k --keep: não apagar ficheiros temporários
    # -d --dir: directório para gravar os outputs
    if not os.path.exists(TMP_DIR):
        os.mkdir(TMP_DIR)

    filename = sys.argv[1]
    outfilename = sys.argv[2]

    if filename.endswith('.pdf'):
        xml_file = pdf2xml(filename)
        pretxt_file = xml2pretxt(xml_file)
        txt_file = pretxt2txt(pretxt_file)
        json_file = txt2json(txt_file)
    elif filename.endswith('.xml'):
        pretxt_file = xml2pretxt(filename)
        txt_file = pretxt2txt(pretxt_file)
        json_file = txt2json(txt_file)
    elif ext == '.pre.txt':
        txt_file = pretxt2txt(filename)
        json_file = txt2json(txt_file)
    elif ext == '.txt':
        json_file = txt2json(filename)
    else:
        print 'Unsupported extension!'
        sys.exit()

    shutil.copyfile(json_file, outfilename)
    # TODO: Remove temp files 
