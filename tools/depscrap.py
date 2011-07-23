# -*- coding: utf-8 -*-
import urllib
from BeautifulSoup import BeautifulSoup
#from BeautifulSoup import BeautifulStoneSoup
from datetime import datetime as dt
from json import dumps
import os
#import sys
from hashlib import sha1

DEFAULT_MAX = 4230

def hash(str):
    hash = sha1()
    hash.update(str)
    return hash.hexdigest()

def file_get_contents(file):
    return open(file).read()
def file_put_contents(file, contents):
    open(file, 'w+').write(contents)

def getpage(url):
    if not os.path.exists('cache'):
        print 'New folder cache/.'
        os.mkdir('cache')
    url_hash=hash(url)
    cache_file='cache/'+url_hash
    
    if os.path.exists(cache_file):
        page=file_get_contents(cache_file)
    else:
        page = urllib.urlopen(url).read()
        file_put_contents(cache_file, page)
    return page

DATASETS = '../../datasets/'
#DATASETS='./'
URL_DEPS_ACTIVOS='http://www.parlamento.pt/DeputadoGP/Paginas/DeputadosemFuncoes.aspx'
FORMATTER_URL_BIO_DEP='http://www.parlamento.pt/DeputadoGP/Paginas/Biografia.aspx?BID=%d'


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

deprows={}

for i in range(0, max):
    #for i in range(2167,2168):
    print i
    url=FORMATTER_URL_BIO_DEP % i
    soup=BeautifulSoup(getpage(url))
    name=soup.find('span',dict(id= 'ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_ucNome_rptContent_ctl01_lblText'))
    short=soup.find('span',dict(id= 'ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_lblNomeDeputado'))
    birthdate=soup.find('span',dict(id= 'ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_ucDOB_rptContent_ctl01_lblText'))
    party=soup.find('span',dict(id= 'ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_lblPartido'))
    #ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_pnlProf
    profession=soup.find('div',dict(id= 'ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_pnlProf'))
    #ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_pnlHabilitacoes
    literacy=soup.find('div',dict(id= 'ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_pnlHabilitacoes'))
    #ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_pnlCargosExercidos
    jobs=soup.find('div',dict(id= 'ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_pnlCargosExercidos')) # ;)
    #ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_pnlComissoes
    coms=soup.find('div',dict(id= 'ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_pnlComissoes'))
    #ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_gvTabLegs
    legs=soup.find('table',dict(id= 'ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_gvTabLegs'))
    if name:
        deprows[i]= {'id': i,
                     'name': name.text,
                     'url': url,
                     'date': dt.utcnow().isoformat()}
        if short:
            deprows[i]['short']=short.text
        if birthdate:
            deprows[i]['birthdate']=birthdate.text
        if party:
            deprows[i]['party']=party.text
        if profession:
            #TODO: break professions string into multiple entries, ';' is the separator
            #TODO: these blocks are repeated and should be made into functions
            deprows[i]['profession']=[]
            for each in profession.findAll('tr')[1:]:
                deprows[i]['profession'].append(each.text)
        if literacy:
            deprows[i]['literacy']=[]
            for each in literacy.findAll('tr')[1:]:
                deprows[i]['literacy'].append(each.text)
        if jobs:
            deprows[i]['jobs']=[]
            for each in jobs.findAll('tr')[1:]:
                deprows[i]['jobs'].append(each.text)
        if coms:
            deprows[i]['coms']=[]
            for each in coms.findAll('tr')[1:]:
                deprows[i]['coms'].append(each.text)
        if legs:
            deprows[i]['legs']=[]
            for each in legs.findAll('tr')[1:]:
                leg=each.findAll('td')
                deprows[i]['legs'].append({'desc': leg[0].text, 'circulo': leg[3].text, 'grupo': leg[4].text})

depsfp = open(DATASETS + 'deputados.json', 'w+')
depsfp.write(dumps(deprows, encoding='utf-8', indent=1, sort_keys=True))
depsfp.close()

#print dumps(deprows, encoding='utf-8', indent=1, sort_keys=True)






