#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
Conjunto de unit tests para o QDizem.

Aqui incluímos vários excertos de intervenções, de forma a assegurar que estão
bem implementados e que devolvem os valores esperados.

'''

import unittest
from qdizem import QDParser


class FirstTest(unittest.TestCase):
    def setUp(self):
        self.qdp = QDParser()

    def tearDown(self):
        del self.qdp

    def test(self):
        intext = 'O Sr. João Oliveira (PCP): — Muito bem!\n'
        outtext = 'João Oliveira|PCP|Muito bem!\n'
        
        self.qdp.open_from_string(intext)
        self.qdp.run()
        output = self.qdp.get_csv_output()
        self.failUnless(output == outtext)
    
    def testAplausos(self):
        intext = '''O Sr. José Moura Soeiro (BE): — Teste.
Aplausos do BE.
Frase teste.
'''
        outtext = '''José Moura Soeiro|BE|Teste.
|BE|*** Aplausos ***
Frase teste.        
'''

        self.qdp.open_from_string(intext)
        self.qdp.run()
        output = self.qdp.get_csv_output()
        print 'Expected:'
        print '    ' + outtext
        print 'Got:'
        print '    ' + output
        self.failUnless(output == outtext)

if __name__ == '__main__':
    unittest.main()
