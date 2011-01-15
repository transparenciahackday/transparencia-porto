#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Script para criar os modelos do Django a partir das transcrições do DAR
Copyright 2010-2011 Ricardo Lafuente <r@sollec.org>

Licenciado segundo a GPL v3
http://www.gnu.org/licenses/gpl.html
'''


### Set up Django path
import sys, os
projectpath = os.path.abspath('../../')
if projectpath not in sys.path:
    sys.path.append(projectpath)
    sys.path.append(os.path.join(projectpath, 'dptd/'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'dptd.settings'

import csv
import datetime, time
import dateutil.parser

from dptd.deputados.models import MP, Party, GovernmentPost
from dptd.dar.models import Entry, Day
from dptd.settings import TRANSCRIPTS_DIR

print 'A calcular palavras preferidas...'
for mp in MP.objects.all():
    mp.calculate_favourite_word()
for mp in MP.objects.exclude(favourite_word=None):
    print "<b>" + mp.shortname + "</b> (" + mp.current_party.abbrev + "): <i>" + mp.favourite_word + "</i>"
