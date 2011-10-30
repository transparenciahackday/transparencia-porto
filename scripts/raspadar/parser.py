#!/usr/bin/env python
# -*- coding: utf-8 -*-

from html2text import parse_html_file
from txt2taggedtext import parse_txt_file

from txt2csv import parse_tagtxt_file_to_csv
from txt2json import parse_tagtxt_file_to_json

def parse_file(filename):
    if filename.endswith('.html'):
        print 'file is html'
    elif filename.endswith('.tag.txt'):
        print 'file is tagged txt'
    elif filename.endswith('.txt'):
        print 'file is txt'
    elif filename.endswith('.csv'):
        print 'file is csv'
    elif filename.endswith('.json'):
        print 'file is json'


def run_tests():
    pass

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    parse_file(filename)
