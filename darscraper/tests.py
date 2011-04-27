#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from BeautifulSoup import BeautifulSoup
import html2text
import unittest

TESTFILE_DIR = 'testfiles/'
FILE_LINEBREAKS = 'testfiles/basic.html'
FILE_LINEBUG = 'testfiles/linebug.html'

def diff(s1, s2):
    import difflib
    # from difflib_data import *

    d = difflib.Differ()
    diff = d.compare(s1, s2)
    ldiff = list(diff)
    for item in ldiff:
        if item.startswith(' '):
            item = item.strip(' ')
    print ''.join(ldiff)

class TestHTMLParsing(unittest.TestCase):

    def setUp(self):
        self.parser = html2text.QDSoupParser()

    def _test_file(self, name):
        infile = os.path.join(TESTFILE_DIR, name) + '.html'
        controlfile = os.path.join(TESTFILE_DIR, name) + '.txt'
        outfile = os.path.join(TESTFILE_DIR, name) + '-out.txt'

        html = open(infile)
        soup = BeautifulSoup(html)

        self.parser.parse_soup(soup)
        self.parser.clean_statements()
        self.parser.clean_statements()
        self.parser.clean_statements()

        txt = self.parser.get_txt()

        out = open(outfile, 'w')
        out.write(txt)
        out.close()

        result = open(outfile).read()
        control = open(controlfile).read()
        try:
            self.assertEqual(txt, control)
        except AssertionError:
            print '  ---- Generated text ---- '
            print
            print result
            print
            print '  ---- Expected text ----'
            print
            print control
            print
            raise

    def test_linebreaks(self):
        '''basic.html: Assegura que as quebras de linha são feitas como deve ser.'''
        self._test_file('basic')

    def test_linebug(self):
        '''linebug.html: Correcção de quebras de linha esquecidas pelos redactores.'''
        self._test_file('linebug')

    def test_acentos(self):
        '''acentos.html: Correcção de erros de OCR no reconhecimento de caracteres com acentos.'''
        self._test_file('acentos')

    def test_pm(self):
        '''pm.html: Detecção e catalogação de intervenções do PM.'''
        self._test_file('pm')

    def test_pontuacao(self):
        '''pontuacao.html: Detecção de pontuação sem espaço a seguir.'''
        self._test_file('pontuacao')

class TestTextParsing(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()

