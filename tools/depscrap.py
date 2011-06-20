# -*- coding: utf-8 -*-
import urllib
from BeautifulSoup import BeautifulSoup
#from BeautifulSoup import BeautifulStoneSoup
from datetime import datetime as dt
from json import dumps
#import os
#import sys
from hashlib import sha1

DEFAULT_MAX = 4230

def hash(str):
    hash = sha1()
    hash.update(str)
    return hash.hexdigest()

def getpage(url):
    page = urllib.urlopen(url).read()
    return page

DATASETS = '../../datasets/'
#DATASETS='./'
URL_DEPS_ACTIVOS='http://www.parlamento.pt/DeputadoGP/Paginas/DeputadosemFuncoes.aspx'
FORMATTER_URL_BIO_DEP='http://www.parlamento.pt/DeputadoGP/Paginas/Biografia.aspx?BID=%d'

print 'Pulling active Deps to calculate a max range of IDs to brute force...'

try:
    deps_activos_list = getpage(URL_DEPS_ACTIVOS)
    soup = BeautifulSoup(deps_activos_list)
except: # há muitos erros http ou parse que podem ocorrer
    soup = None
    print 'Active MP page could not be fetched. Using a max ID value of %d.' % DEFAULT_MAX 

if soup:
    max = 0
    table_deps = soup.find('table', 'ARTabResultados')
    deps = table_deps.findAll('tr', 'ARTabResultadosLinhaPar')
    deps += table_deps.findAll('tr', 'ARTabResultadosLinhaImpar')
    for dep in deps:
        depurl = dep.td.a['href']
        dep_bid = int(depurl[depurl.find('BID=')+4:])
        if dep_bid > max:
            max = dep_bid
    max = int(max * 1.05)
else:
    max = int(DEFAULT_MAX * 1.05)

print 'Testing up to %d' % max

deprows = []

for i in range(0, max):
    #for i in range(100,103):
    print i
    soup = BeautifulSoup(getpage(FORMATTER_URL_BIO_DEP % i))
    name = soup.find('span',dict(id= 'ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_ucNome_rptContent_ctl01_lblText'))
    if name:
        deprows.append({'id': i,
                        'name': name.text,
                        'date': dt.utcnow().isoformat()})

depsfp = open(DATASETS + 'deputados.json', 'w+')
depsfp.write(dumps(deprows, encoding='utf-8', indent=1))
depsfp.close()












