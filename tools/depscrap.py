# -*- coding: utf-8 -*-
import urllib
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import csv
import os
import shelve
import sys

def getpage(url):
    return urllib.urlopen(url).read()

s=shelve.open('cache.shelve')

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
max*=1.05
print 'Testing up to %d' % max

#s['bios']={}
#for i in range(max):
for i in range(100,110):
    soup=BeautifulSoup(getpage(FORMATTER_URL_BIO_DEP % i))
    print soup.find('span',dict(id= 'ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_ucNome_rptContent_ctl01_lblText')).text
    print '##########'

#s.sync()
#s.close()













