#!/usr/bin/env python
# -*- coding: utf-8 -*-

TMP_DIR = "./temp"

import sys, os, shutil

def pdf2xml(filename, verbose=False):
    outfilename = os.path.join(TMP_DIR, os.path.basename(filename).replace('.pdf', '.xml'))
    if verbose: print "%s: Converting PDF to XML into file %s" % (filename, outfilename)
    os.system("python pdf2xml.py -o %s %s" % (outfilename, filename))
    return outfilename

def xml2pretxt(filename, verbose=False):
    outfilename = os.path.join(TMP_DIR, os.path.basename(filename).replace('.xml', '.pre.txt'))
    if verbose: print "%s: Converting XML to text into file %s" % (filename, outfilename)
    os.system("python xml2txt.py %s %s" % (filename, outfilename))
    return outfilename

def pretxt2txt(filename, verbose=False):
    outfilename = os.path.join(TMP_DIR, os.path.basename(filename).replace('.pre.txt', '.txt'))
    if verbose: print "%s: Post-processing text into file %s" % (filename, outfilename)
    os.system("python txtpostproc.py %s %s" % (filename, outfilename))
    return outfilename

def txt2json(filename, verbose=False):
    outfilename = os.path.join(TMP_DIR, os.path.basename(filename).replace('.txt', '.json'))
    if verbose: print "%s: Structuring text to JSON into file %s" % (filename, outfilename)
    os.system("python txt2json.py %s %s" % (filename, outfilename))
    return outfilename

def run_parse_pipeline(filename, outfilename, keep=False, verbose=False):
    if filename.endswith('.pdf'):
        xml_file = pdf2xml(filename, verbose)
        pretxt_file = xml2pretxt(xml_file, verbose)
        txt_file = pretxt2txt(pretxt_file, verbose)
        json_file = txt2json(txt_file, verbose)
        files_to_delete = [xml_file, pretxt_file, txt_file, json_file]
    elif filename.endswith('.xml'):
        pretxt_file = xml2pretxt(filename, verbose)
        txt_file = pretxt2txt(pretxt_file, verbose)
        json_file = txt2json(txt_file, verbose)
        files_to_delete = [pretxt_file, txt_file, json_file]
    elif filename.endswith('.pre.txt'):
        txt_file = pretxt2txt(filename, verbose)
        json_file = txt2json(txt_file, verbose)
        files_to_delete = [txt_file, json_file]
    elif filename.endswith('.txt'):
        json_file = txt2json(filename, verbose)
        files_to_delete = [json_file]
    else:
        print 'Unsupported extension!'
        sys.exit()
    if verbose: print "%s: Copying JSON file into file %s" % (filename, outfilename)
    # cleanup
    if not keep:
        for f in files_to_delete:
            os.remove(f)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="input filename (.pdf, .xml, .pre.txt or .txt) or dir with PDF files")
    parser.add_argument("outfilename", help="output filename (JSON file) or dir")
    parser.add_argument("-k", "--keep", help="don't delete temporary files", action="store_true")
    parser.add_argument("-v", "--verbose", help="output verbose information", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(TMP_DIR):
        os.mkdir(TMP_DIR)

    filename = args.filename
    outfilename = args.outfilename

    if os.path.isdir(filename) and os.path.isdir(outfilename):
        indir = filename + '/' if not filename.endswith('/') else filename
        outdir = outfilename + '/' if not outfilename.endswith('/') else outfilename
        import glob
        types = ['pdf', 'xml', 'pre.txt', 'txt']
        for t in types:
            for f in glob.glob(indir + '*.%s' % t):
                infile = f
                outfile = os.path.join(outdir, os.path.basename(f).replace('.pdf', '.json'))
                run_parse_pipeline(infile, outfile, keep=args.keep, verbose=args.verbose)
    elif os.path.exists(filename) and outfilename.endswith('.json'):
        # single file
        run_parse_pipeline(filename, outfilename, keep=args.keep, verbose=args.verbose)
    else:
        print 'Wrong input, run with --help for usage'
        sys.exit()

    # TODO: Remove temp files 
