#!/usr/bin/env python
# -*- coding: utf-8 -*-

from html2text import parse_html_file
from txt2taggedtext import parse_txt_file
from txt2csv import parse_tagtxt_file_to_csv
from txt2json import parse_tagtxt_file_to_json

import sys, os

DIRS = {
        'txt': 'txt',
        'tagtxt': 'tagtxt',
        'csv': 'csv',
        'json': 'json',
        }

def replace_extension(filename, newext):
    if filename.endswith('.tag.txt'):
        ext = '.tag.txt'
        basename = filename.replace('.tag.txt', '')
    else:
        basename, ext = os.path.splitext(filename)
    return basename + newext    

def parse_file(filename, continuous=True):
    '''Accepts a filename and processes it into the next logical output format.
    Output format sequence is HTML - txt - tagged txt - json
    If continuous is True, parsing will go on until reaching the end of the sequence.
    '''
    if filename.endswith('.html'):
        print 'Parsing HTML file...'
        outfile = os.path.join(DIRS['txt'], replace_extension(os.path.split(filename)[-1], '.txt'))
        print '  %s -> %s' % (filename, outfile)
        new_file = parse_html_file(filename, outfile)
        print '-> ' + new_file
        if continuous:
            parse_file(new_file)

    elif filename.endswith('.tag.txt'):
        print 'Parsing tagged text file...'
        outfile = os.path.join(DIRS['json'], replace_extension(os.path.split(filename)[-1], '.json'))
        print '-> ' + outfile
        parse_tagtxt_file_to_json(filename, outfile)
        if continuous:
            parse_file(outfile)

    elif filename.endswith('.txt'):
        print 'Parsing text file...'
        outfile = os.path.join(DIRS['tagtxt'], replace_extension(os.path.split(filename)[-1], '.tag.txt'))
        print '-> ' + outfile
        parse_txt_file(filename, outfile)
        if continuous:
            parse_file(outfile)

    elif filename.endswith('.csv'):
        print 'Got CSV file, nothing to parse'
    elif filename.endswith('.json'):
        print 'Got JSON file, nothing to parse'

def run_tests():
    pass

if __name__ == '__main__':
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        parse_file(filename, continuous=False)
    elif len(sys.argv) > 2:
        for filename in sys.argv:
            parse_file(filename, continuous=False)
    else:
        print 'Argh! I need an input file to go on!'
        sys.exit()
