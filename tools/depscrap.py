# -*- coding: utf-8 -*-
import urllib
from BeautifulSoup import BeautifulSoup
#from BeautifulSoup import BeautifulStoneSoup
from datetime import datetime as dt
from json import dumps
import os
import shelve
import sys
from hashlib import sha1

def hash(str):
    hash=sha1()
    hash.update(str)
    return hash.hexdigest()

def getpage(url):
    try:
        page= s[hash(url)]
    except:
        page= urllib.urlopen(url).read()
        s[hash(url)]=page
        s.sync()
    return page

s=shelve.open('cache.shelve')

DATASETS='../../datasets/'

URL_DEPS_ACTIVOS='http://www.parlamento.pt/DeputadoGP/Paginas/DeputadosemFuncoes.aspx'
FORMATTER_URL_BIO_DEP='http://www.parlamento.pt/DeputadoGP/Paginas/Biografia.aspx?BID=%d'

print 'Pulling active Deps to calculate a max range of IDs to brute force...'

if s.has_key('depsactivos'):
    print 'using cached page'
    deps_activos_list=s['depsactivos']
else:
    print 'fetching new page'
    deps_activos_list=getpage(URL_DEPS_ACTIVOS)
    s['depsactivos']=deps_activos_list
    s.sync()
    s.close()

soup=BeautifulSoup(deps_activos_list)
max=0
table_deps = soup.find('table', 'ARTabResultados')
deps=table_deps.findAll('tr', 'ARTabResultadosLinhaPar')
deps+=table_deps.findAll('tr', 'ARTabResultadosLinhaImpar')
for dep in deps:
    depurl=dep.td.a['href']
    dep_bid=int(depurl[depurl.find('BID=')+4:])
    if dep_bid>max:
        max=dep_bid
max=int(max*1.05)
print 'Testing up to %d' % max

deprows=[]

for i in range(0, max):
    print i
    #for i in range(100,103):
    soup=BeautifulSoup(getpage(FORMATTER_URL_BIO_DEP % i))
    name=soup.find('span',dict(id= 'ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_ucNome_rptContent_ctl01_lblText'))
    if name:
        deprows.append({'id': i,
                        'name': name.text,
                        'date': dt.utcnow().isoformat()})

depsfp=open(DATASETS+'deputados.json', 'w')
depsfp.write(dumps(deprows))
depsfp.close()

s.sync()
s.close()













