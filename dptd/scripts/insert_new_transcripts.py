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
from dptd.dar.models import Entry, Day, entry_choices
from dptd.settings import TRANSCRIPTS_DIR

print 'A importar transcrições...'
for root, dirs, files in os.walk(TRANSCRIPTS_DIR):
    for f in files:
        print f
        if not f.endswith('csv'):
            continue
        
        slug = f.split('.')[0]
        dar, leg, sess, number, date = slug.split('_')

        try:
            d = dateutil.parser.parse(date)
        except ValueError:
            d = None

        if not d:
            print 'File %s has a strange date format. Ignoring.' % f
            continue

        if Day.objects.filter(date=date):
            s = Day.objects.get(date=date)
        else:
            s = Day.objects.create(date=date)

        filename = os.path.join(TRANSCRIPTS_DIR, f)

        lines = csv.reader(open(filename), delimiter='|', quotechar='"')

        for mpname, party, text, stype in lines:
            for t in entry_choices:
                if t[0] == stype:
                    stype = t[1]
            if type(stype) != int:
                print 'Statement type "%s" not recognised.' % str(stype)
                stype = None
            if len(mpname) > 200:
                mpname = mpname[200:]
            if len(party) > 200:
                party = party[200:]
            matching_mps = MP.objects.filter(shortname=mpname)
            if matching_mps:
                if len(matching_mps) > 1:
                    # more than 1 result for this MP's shortname
                    # use the party to determine this
                    if Party.objects.filter(abbrev=party):
                        p = Party.objects.get(abbrev=party)
                    else:
                        print 'Party "%s" not recognised.' % party
                    try:
                        mp = MP.objects.get(shortname=mpname, caucus__party=p)
                    except:
                        print 'More than 1 result for name %s in party %s. Not assigning MP instance.' % (mpname, party)
                        Entry.objects.create(speaker=mpname, party=party, text=text, type=stype, day=s)
                else:
                    mp = MP.objects.get(shortname=mpname)
                Entry.objects.create(mp=mp, party=party, text=text, type=stype, day=s)
            else:
                if GovernmentPost.objects.filter(name=mpname):
                    mp = MP.objects.get(governmentpost__name=mpname)
                    Entry.objects.create(mp=mp, party=party, text=text, type=stype, day=s)
                else:
                    Entry.objects.create(speaker=mpname, party=party, text=text, type=stype, day=s)

print 'A calcular palavras preferidas...'
for mp in MP.objects.all():
    mp.calculate_favourite_word()
