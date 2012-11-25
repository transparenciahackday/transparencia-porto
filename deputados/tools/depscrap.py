#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
depscrap
========

Descarrega a página de um deputado do Parlamento.pt e extrai uma parte da informação, convertendo para JSON.
Também obtém a lista de deputados em funções caso não seja indicado um intervalo de ID's.

Como usar
---------

Gravar o resultado num ficheiro:
    python depscrap -o deputados.json

Gravar o resultado num ficheiro com uma indentação de 4 espaços:
    python depscrap -o deputados.json -i 4

Para mostrar o resultado na linha de comandos:
    python depscrap

Para ver todas as opções possíveis:
    python depscrap -h

Ver também
----------
* interessesscrap.py
* pic_scrapper.py

"""
#
import urllib
from BeautifulSoup import BeautifulSoup
#from BeautifulSoup import BeautifulStoneSoup
from datetime import datetime as dt
from json import dumps
from utils import *
#import sys
from replaces_depscrap import SHORTNAME_REPLACES


DEFAULT_MAX = 4600

ROMAN_NUMERALS = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
    'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
    'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15,
    'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20,
    'XXI': 21, 'XXII': 22, 'XXIII': 23, 'XXIV': 24, 'XXV': 25,
    }

DATASETS = '../../datasets/'
URL_DEPS_ACTIVOS='http://www.parlamento.pt/DeputadoGP/Paginas/DeputadosemFuncoes.aspx'
FORMATTER_URL_BIO_DEP='http://www.parlamento.pt/DeputadoGP/Paginas/Biografia.aspx?BID=%d'

def parse_legislature(s):
    s = s.replace('&nbsp;', '')
    number, dates = s.split('[')
    number = ROMAN_NUMERALS[number.strip()]
    dates = dates.strip(' ]')
    if len(dates.split(' a ')) == 2:
        start, end = dates.split(' a ')
    else:
        start = dates.split(' a ')[0]
        end = ''
    if start.endswith(' a'):
        start = start.replace(' a', '')
    return number, start, end

def scrape(start=1, end=None, verbose=False, outfile='', indent=1):
    if not end:
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
    else:
        max = end
    
    deprows = {}
    
    for i in range(start, max):
        if verbose: print i
        url = FORMATTER_URL_BIO_DEP % i
        soup = BeautifulSoup(getpage(url))
        name = soup.find('span',dict(id='ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_ucNome_rptContent_ctl01_lblText'))
        short = soup.find('span',dict(id='ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_lblNomeDeputado'))
        birthdate = soup.find('span',dict(id='ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_ucDOB_rptContent_ctl01_lblText'))
        party = soup.find('span',dict(id='ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_lblPartido'))
        occupation = soup.find('div',dict(id='ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_pnlProf'))
        education = soup.find('div',dict(id='ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_pnlHabilitacoes'))
        current_jobs = soup.find('div',dict(id='ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_pnlCargosDesempenha')) # ;)
        jobs = soup.find('div',dict(id='ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_pnlCargosExercidos')) # ;)
        awards = soup.find('div',dict(id='ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_pnlCondecoracoes')) 
        coms = soup.find('div',dict(id='ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_pnlComissoes'))
        mandates = soup.find('table',dict(id='ctl00_ctl13_g_8035397e_bdf3_4dc3_b9fb_8732bb699c12_ctl00_gvTabLegs'))
        if name:
            deprows[i]= {'id': i,
                         'name': name.text,
                         'url': url,
                         'scrape_date': dt.utcnow().isoformat()}
            if short:
                # replace by canonical shortnames if appropriate
                if short.text in SHORTNAME_REPLACES:
                    t = SHORTNAME_REPLACES[short.text]
                else:
                    t = short.text
                deprows[i]['shortname'] = t
            if birthdate:
                deprows[i]['birthdate'] = birthdate.text
            if party:
                deprows[i]['party'] = party.text
            if education:
                #TODO: break educations string into multiple entries, ';' is the separator
                #TODO: these blocks are repeated and should be made into functions
                deprows[i]['education'] = []
                for each in education.findAll('tr')[1:]:
                    text = each.find('span').text
                    deprows[i]['education'].append(text)
            if occupation:
                deprows[i]['occupation'] = []
                for each in occupation.findAll('tr')[1:]:
                    deprows[i]['occupation'].append(each.text)
            if jobs:
                deprows[i]['jobs'] = []
                for each in jobs.findAll('tr')[1:]:
                    if '\n' in each.text:
                        for j in each.text.split('\n'):
                            if j:
                                deprows[i]['jobs'].append(j.rstrip(' .;'))
                    else:
                        deprows[i]['jobs'].append(each.text)
            if current_jobs:
                deprows[i]['current_jobs'] = []
                for each in current_jobs.findAll('tr')[1:]:
                    if '\n' in each.text:
                        for j in each.text.split('\n'):
                            if j:
                                deprows[i]['current_jobs'].append(j.rstrip(' .;'))
                    else:
                        deprows[i]['current_jobs'].append(each.text.rstrip(' ;.'))
            if coms:
                deprows[i]['commissions'] = []
                for each in coms.findAll('tr')[1:]:
                    deprows[i]['commissions'].append(each.text)
            if awards:
                deprows[i]['awards'] = []
                for each in awards.findAll('tr')[1:]:
                    if '\n' in each.text:
                        for j in each.text.split('\n'):
                            if j:
                                deprows[i]['awards'].append(j.rstrip(' .;'))
                    else:
                        deprows[i]['awards'].append(each.text.rstrip(' ;.'))
            if mandates:
                deprows[i]['mandates'] = []
                for each in mandates.findAll('tr')[1:]:
                    leg = each.findAll('td')
                    l = leg[0].text
                    number, start, end = parse_legislature(l)

                    deprows[i]['mandates'].append({'legislature': number, 'start_date': start, 'end_date': end, 'constituency': leg[3].text, 'party': leg[4].text})

            if verbose:
                print name
    
    if outfile:
        depsfp = open(outfile, 'w+')
        depsfp.write(dumps(deprows, encoding='utf-8', indent=indent, sort_keys=True))
        depsfp.close()
    else:
        print dumps(deprows, encoding='utf-8', indent=indent, sort_keys=True)


if __name__ == '__main__':
    import sys 
    import optparse
    parser = optparse.OptionParser()
    # TODO: Add an option to overwrite cache, in order to get up-to-date records
    parser.add_option('-s', '--start', 
                      dest="start", 
                      help='Begin parsing from this ID (int required)'
                      )
    parser.add_option('-e', '--end', 
                      dest="end ", 
                      help='Stop parsing on this ID (int required)'
                      )
    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help='Print verbose information',
                      )
    parser.add_option('-o', '--outfile', 
                      dest=" outfile", 
                      default="",
                      help='Output JSON to this file'
                      )
    parser.add_option('-i', '--indent', 
                      dest="indent", 
                      default="1",
                      help='Number of spaces for indentation (default is 1)'
                      )

    options, remainder = parser.parse_args()
    start = int(options.start)
    end = int(options.end)
    verbose = options.verbose
    outfile = options.outfile
    indent = options.indent

    scrape(start, end, verbose, outfile, indent)



