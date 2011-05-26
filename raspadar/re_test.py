#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import locale
from html2text import strip_accents
locale.setlocale(locale.LC_ALL, 'pt_PT.UTF8')

strings = [u'O Sr. Presidente : – Inscreveram-se',
           u'O Sr. Bernardino Jimbras (PCP):– Inscreveram-se',
           u'O Sr. Ministro da Administração Interna (Jorge Lacão): – Hai',
           u'O Orador: - Ora viva!'
           ]

# o \w não está a reconhecer palavras com acentos!
re_cont = (re.compile(ur'O Orador|A Oradora(?P<sep>\:[ \.]?[\–\–\—\-])', re.UNICODE, '')
re_interv = (re.compile(ur'^(?P<titulo>O Sr\.|A Sr\.(ª)?)\ ?(?P<nome>[\w ]+)\ (?P<partido>\([\w ]+\))?(?P<sep>\:[ \.]?[\–\–\—\-])', re.UNICODE), '')
# re_interv = (re.compile(ur'^(?P<titulo>O Sr\.|A Sr\.(ª)?)\ ?(?P<nome>([A-ZdÁ][a-z\-ç\'é ]+\b|Álvaro)+)\ (?P<partido>\([A-Za-z]+\))?(?P<sep>\:[ \.]?[\–\–\—\-])', re.LOCALE|re.UNICODE), '')

for s in strings:
    m = re.search(re_interv[0], s)
    # print re.sub(re_interv[0],re_interv[1], s)

    if m:
        print m.group('titulo')
        print m.group('nome')
        if m.group('partido'):
            print m.group('partido').strip('()')
    else:
        print 'Not matched: ' + s
