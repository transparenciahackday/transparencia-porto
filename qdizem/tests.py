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
        
    def parse_this(self, intext, outtext):
        # função para comparar dois strings e não passar o teste caso
        # sejam diferentes
        self.qdp.open_from_string(intext)
        self.qdp.run()
        output = self.qdp.get_csv_output()
        try:
            self.failUnless(output == outtext)    
        except AssertionError:
            print 'Expected:'
            print '----------------------'
            print outtext
            print '----------------------'            
            print 'Got:'
            print '----------------------'
            print output
            print '----------------------'     
            raise       

    def testBasic(self):
        intext = 'O Sr. João Oliveira (PCP): — Muito bem!\n'
        outtext = 'João Oliveira|PCP|Muito bem!\n'
        self.parse_this(intext, outtext)
        
    def testAplausos(self):
        intext = '''O Sr. José Moura Soeiro (BE): — Teste.
Aplausos do BE.
Frase teste.
'''
        outtext = '''José Moura Soeiro|BE|Teste.
|BE|*** Aplausos ***
||Frase teste.
'''
        self.parse_this(intext, outtext)

    def testAplausos2(self):
        intext = '''O Sr. José Moura Soeiro (BE): — Teste.
Aplausos do BE.
O Sr. José Moura Soeiro (BE): — Teste dois.
'''
        outtext = '''José Moura Soeiro|BE|Teste.
|BE|*** Aplausos ***
José Moura Soeiro|BE|Teste dois.
'''
        self.parse_this(intext, outtext)
        
    def testPresidente(self):
        intext = 'O Sr. Presidente: — Teste.\n'
        outtext = 'Presidente|Presidente|Teste.\n'
        self.parse_this(intext, outtext)
    
    def testPresidenteAlternativo(self):
        intext = 'A Sr.ª Presidente (Teresa Caeiro): — Teste.\n'
        outtext = 'Teresa Caeiro|Presidente|Teste.\n'
        self.parse_this(intext, outtext)

if __name__ == '__main__':
    unittest.main()
