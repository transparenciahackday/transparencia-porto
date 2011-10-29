#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import locale
locale.setlocale(locale.LC_ALL, 'pt_PT.UTF8')

strings = [u'O Sr. Presidente : – Inscreveram-se',
           u'O Sr. Bernardino Jimbras (PCP):– Inscreveram-se',
           u'O Sr. Ministro da Administração Interna (Jorge Lacão): – Hai',
           u'O Sr. Deputado sabe: é assim',
          ]
# [[:upper:]d][]
re_separador = (re.compile(ur'\:?[ \.]?[\–\–\—\-] ', re.LOCALE|re.UNICODE), ': -')
re_separador_estrito = (re.compile(ur'\: [\–\–\—\-] ', re.LOCALE|re.UNICODE), ': - ')

re_interv_semquebra = (re.compile(ur'(?P<titulo>O Sr\.?|A Sr(\.)?(ª)?)\ (?P<nome>[\w ,’-]{1,50})\ ?(?P<partido>\([\w -]+\))?(?P<sep>\:?[ \.]?[\–\–\—\-] )', re.UNICODE), '')


re_titulo = (re.compile(ur'((O Sr[\.:])|(A Sr\.?(ª)?))(?!( Deputad))'), '')

for s in strings:
    m = re.search(re_titulo[0], s)
    print m
    if m:
        print m.group()
        print m.groups()



'''
for s in strings:
    m = re.search(re_concluir[0], s)
    # print re.sub(re_interv[0],re_interv[1], s)

    if m:
        print m.group()
        print m.groups()
        # if m.group('partido'):
            # print m.group('partido').strip('()')
    # else:
        # print 'Not matched: ' + s
'''
