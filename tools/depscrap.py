# -*- coding: utf-8 -*-
import urllib
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import csv
import os
import shelve
import sys
from taskqueue import Queue
from taskqueue import Task

def getpage(url):
    return urllib.urlopen(url).read()

s=shelve.open('cache.shelve')
q=Queue()

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

s['bios']={}
#for i in range(max):
for i in range(100,110):
    q.append(Task(getpage, (FORMATTER_URL_BIO_DEP % i,)))

while not q.is_empty():
    uo=q.pop
    if uo.getcode() != 200:
        break
    
    soup=BeautifullSoup(uo.read())
    print soup ### omg omg omg, need to commit


q.wait()
q.die()
s.sync()
s.close()













