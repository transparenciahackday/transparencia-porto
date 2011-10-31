#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from BeautifulSoup import BeautifulSoup
import html2text, txt2taggedtext
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
        self.maxDiff = None
        self.html_parser = html2text.QDSoupParser()
        self.txt_tagger = txt2taggedtext.RaspadarTagger()

    def tearDown(self):
        pass

    def _test_file(self, name, get_metadata=False):
        infile = os.path.join(TESTFILE_DIR, name) + '.html'
        controlfile = os.path.join(TESTFILE_DIR, name) + '.txt'
        outfile = os.path.join(TESTFILE_DIR, name) + '-out.txt'

        html = open(infile)
        soup = BeautifulSoup(html)

        self.html_parser.run(soup, get_date=False)
        txt = self.html_parser.get_txt()

        import codecs
        out = codecs.open(outfile, 'w', 'utf-8')
        out.write(txt)
        out.close()

        result = codecs.open(outfile, 'r', 'utf-8').read()
        control = codecs.open(controlfile, 'r', 'utf-8').read()

        #os.remove(outfile)
        try:
            self.assertEqual(result, control)
        except AssertionError:
            '''
            print '== Error parsing HTML to txt in test "%s" ==' % name
            print '----------- Generated text (%s) -------- ' % name
            print result
            print '----------------------------------------'
            print
            print '----------- Expected text (%s) -------- ' % name
            print control
            print '----------------------------------------'
            print
            '''
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
        
    def test_intro(self):
        '''metadata.html: Processamento da introdução (sumário, info da sessão), aparar as linhas.'''
        self._test_file('metadata', get_metadata=True)

class TestTextParsing(unittest.TestCase):
    pass

from html2text import is_full_name

NAMES = [u'Teresa Maria Neto Venda',
         u'Emídio Guerreiro',
         u'Álvaro Cósta',
         u'João Chulé',
         u"Diogo d'Ávila"
         u'Duarte Rogério Matos Ventura Pacheco']

NOT_NAMES = [u'Partido Social Democrata (PSD):',
             u'Sr. Primeiro-Ministro',
             u'O Deputado acha']

class TestUtils(unittest.TestCase):
    def test_name(self):
        for name in NAMES:
            try:
                self.assertTrue(is_full_name(name))
            except:
                print 'Full name test - False negative: %s' % name
                raise
        for name in NOT_NAMES:
            try:
                self.assertFalse(is_full_name(name))
            except:
                print 'Full name test - False positive: %s' % name
                raise



if __name__ == '__main__':
    unittest.main()

