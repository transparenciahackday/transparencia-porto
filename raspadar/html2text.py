#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(level=logging.DEBUG)

from BeautifulSoup import BeautifulSoup, NavigableString
import os
import string
import datetime
import re

import locale
locale.setlocale(locale.LC_ALL, 'pt_PT.UTF8')

from pprint import pprint

LOWERCASE_LETTERS = string.lowercase + 'áàãâéèêíìóòõôúùç'

SUMMARY_STRINGS = ('SUMÁRIO', 'S U M Á R I O', 'SUMÁRI0', 'SUMARIO')
TITLES = ('Secretários: ', 'Ex.mos Srs. ', 'Ex. mos Srs. ', 'Exmos Srs. ', 'Ex.. Srs. ', 'Ex.mos. Srs. '
          'Presidente: ', 'Ex.mo Sr. ', 'Exmo. Sr. ', 'Ex.. Sr.', 'Ex.mo. Sr. '
          )

MESES = {
    'JANEIRO': 1,
    'FEVEREIRO': 2,
    'MARÇO': 3,
    'ABRIL': 4,
    'MAIO': 5,
    'JUNHO': 6,
    'JULHO': 7,
    'AGOSTO': 8,
    'SETEMBRO': 9,
    'OUTUBRO': 10,
    'NOVEMBRO': 11,
    'DEZEMBRO': 12,
    }

NUMEROS_ROMANOS = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
    'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
    'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15,
    'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20,
    'XXI': 21, 'XXII': 22, 'XXIII': 23, 'XXIV': 24, 'XXV': 25,
    }

MP_STATEMENT = 'mp'
GOV_STATEMENT = 'gov'
PM_STATEMENT = 'pm'
PRESIDENT_STATEMENT = 'president'
STATEMENT = 'statement'
INTERRUPTION = 'interruption'
APPLAUSE = 'applause'
PROTEST = 'protest'
LAUGHTER = 'laughter'
NOTE = 'note'
PAUSE = 'pause'
VOTE = 'vote'
SECRETARY = 'secretary'
OTHER = 'other'

### Regexes para detecção de erros de OCR ###

# o carácter 'é' às vezes é lido como 'ç', temos de substituir onde não bater certo
# presumimos que se não for seguido por certas vogais, é erro de OCR
re_cedilha = r'ç(?P<char>[^(aouãâáàóòõôúù)])'
# o mesmo para o carácter 'ú', que é mal lido como 'õ'
# se não for seguido de um e ('õe'), presumimos que é erro
re_otil = r'õ(?P<char>[^(e)])'
# acrescentar espaços à frente da pontuação onde faltam
# procura exemplos como ".Á", ",é" mas não ".R." (pode ser uma sigla)
# no entanto omitimos ".a", por causa de "Sr.as"
re_pontuacao = r'(?P<pont>[.,?!])(?P<char>[A-Zb-zÁÀÉÍÓÚ][^.])'
# nomes próprios portugueses
re_nome = r" ?[A-ZdÁ][a-z\-ç'(é )]+\b|Álvaro"
# data da sessão
re_data = r'REUNIÃO PLENÁRIA DE (?P<day>[0-9]{1,2}) DE (?P<month>[A-Z]+) DE (?P<year>[0-9]{4})'

re_c = re.compile(re_cedilha, re.LOCALE|re.UNICODE|re.MULTILINE)
re_ot = re.compile(re_otil, re.LOCALE|re.UNICODE|re.MULTILINE)
re_pont = re.compile(re_pontuacao, re.LOCALE|re.UNICODE|re.MULTILINE)
re_n = re.compile(re_nome, re.LOCALE|re.UNICODE|re.MULTILINE)
re_d = re.compile(re_data, re.LOCALE|re.UNICODE|re.MULTILINE)


# marcador de intervenção
re_intervencao = r'.*:[ .]?[-—] ?.*'
re_interv = re.compile(re_intervencao, re.LOCALE|re.UNICODE|re.MULTILINE)

def remove_strings(st, strings_tuple):
    for s in strings_tuple:
        st = st.replace(s, '')
    return st

def add_item(s, item):
    if type(item) == list:
        logging.warning('List found inside statements. Only strings should be there. Concatenating.')
        for i in item:
            add_item(s, i)
    elif type(item) == str:
        s += item
    else:
        logging.warning('Unexpected object inside statements (%s)' % str(type(item)))
    return s

def strip_accents(s):
    import unicodedata
    new_s = str(s)
    new_s = new_s.decode('UTF-8')
    new_s = ''.join((c for c in unicodedata.normalize('NFD', new_s) if unicodedata.category(c) != 'Mn'))
    return new_s.encode('UTF-8')

def is_full_name(s):
    # Devolve True se a cadeia for um nome de pessoa
    s = s.strip('\n ')
    stripped_s = strip_accents(s)
    non_matches = re.split(re_n, stripped_s)

    for item in non_matches:
        if item.strip():
            return False
    return True
    

def parse_file(infile, outfile):
    f = infile
    html = open(f, 'r')
    soup = BeautifulSoup(html)
    parser = QDSoupParser()
    try:
        parser.run(soup)
    except:
        logging.error('Parsing error in file %s.' % (f))
        raise

    # Apanhar data, só a data (o resto vem no txt2taggedtxt)
    # if parser.date:
        # outfile += '_' + str(parser.date)
    # else:
        # logging.error('Session date not found.')
        # sys.exit()

        ext = '.txt'
    outfile = open(outfile, 'w')
    outfile.write(parser.get_txt())
    outfile.close()

class QDSoupParser:
    def __init__(self):
        self.date = None
        self.summary = None
        self.start_time = None
        self.end_time = None
        self.president = None
        self.secretaries = []
        self.paragraphs = []

    def parse_soup(self, soup):
        output = ''
        self.paragraphs = []
        started = False
        for page in soup.findAll('body'):
            # exclude the first paragraph, but not in the first page
            if started:
                paras = page.findAll('p')[1:]
            else:
                paras = page.findAll('p')
                started = True

            first = True
            for para in paras:
                if para.contents:
                    if len(para.contents) > 1:
                        p = ''
                        for el in para.contents:
                            if type(el) == NavigableString:
                                # text
                                text = el.strip('\n').strip()
                                text = text.replace('\n', ' ').strip()
                                p += text
                            elif el.name == 'br':
                                # line break
                                p += '\n'
                            elif el.name == 'sup':
                                text = el.contents[0].strip(' \n')
                                p += text
                            elif not el:
                                continue
                            else:
                                logging.warning('Unidentified paragraph element found in HTML.')
                                logging.warning('-> %s' % el)
                        self.parse_paragraph(p, first=first)
                    else:
                        el = para.contents[0]
                        p = el.strip('\n').strip()
                        p = p.replace('\n', ' ')
                        if p == '&nbsp;':
                            continue
                        self.parse_paragraph(p, first=first)
                else:
                    assert False
                first = False

    def parse_paragraph(self, p, first=False, skip_encode=False):
        if skip_encode:
            text = p
        else:
            text = p.encode('utf-8')

        text = text.strip(' \n')

        if first:
            # primeiro parágrafo da página, pode ser continuação do anterior.
            # verificar se começa com minúscula e/ou se o anterior não termina com
            # ponto final (excepto casos como 'Sr.').
            if self.paragraphs:
                prev_para = self.paragraphs[-1].strip(' \n')
                if text.startswith(LOWERCASE_LETTERS) or \
                        (not prev_para.endswith(('.', '?', '!', ':')) and not is_full_name(prev_para.split('\n')[-1].strip('\n .'))):
                    if not text.startswith(('O Sr.', 'A Sr', 'O Orador:', 'A Oradora:')) and not text.startswith(('Deputados que', 'Acta')):
                        # print '### Found orphan paragraph. ###'
                        # print text
                        # print 'Previous: ' + prev_para
                        # print
                        if prev_para.endswith('-'):
                            # quebra de palavra
                            self.paragraphs[-1] = prev_para.strip('-') + text
                        else:
                            self.paragraphs[-1] = prev_para + ' ' + text
                        return
        text = text.replace('&nbsp;', '')
        self.paragraphs.append(text)

    def get_date(self):
        for p in self.paragraphs:
            pass
            # if matches date RE
            # save the date, else raise error

    def get_txt(self):
        output = ''
        for s in self.paragraphs:
            if not s.strip('\n '):
                continue
            if not type(s) == str:
                for item in s:
                    output += s + '\n\n'
            elif s:
                output += s + '\n\n'
        return output

    def run(self, soup):
        self.parse_soup(soup)

if __name__ == '__main__':
    import sys
    from ConfigParser import SafeConfigParser

    # analisar o ficheiro config
    parser = SafeConfigParser()
    parser.read('raspadar.conf')
    default_input = os.path.abspath(parser.get('html2txt', 'sourcedir'))
    default_output = os.path.abspath(parser.get('html2txt', 'targetdir'))

    # analisar as opções da linha de comandos
    import optparse
    print 'ARGV      :', sys.argv[1:]
    parser = optparse.OptionParser()
    parser.add_option('-i', '--input', 
                      dest="input", 
                      default="",
                      help='Input file or directory'
                      )
    parser.add_option('-o', '--output', 
                      dest="output", 
                      default="",
                      help='Output file or directory'
                      )
    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help='Print verbose information',
                      )
    options, remainder = parser.parse_args()
    input = options.input
    verbose = options.verbose
    output = options.output

    # verificar se input existe
    if not os.path.exists(input):
        print 'Input not found: ' + str(input)
    # tanto input como output têm de ser ambos ficheiros ou ambos directórios
    if (os.path.isfile(input) and os.path.isdir(output)) or (os.path.isdir(input) and os.path.isfile(output)):
        print 'Input and output must be both filenames or both directory names.'
        print 'Input - File: %s. Dir: %s.' % (str(os.path.isfile(input)), str(os.path.isdir(input)))
        print 'Output - File: %s. Dir: %s.' % (str(os.path.isfile(input)), str(os.path.isdir(input)))
        sys.exit()
    # há input e não output? gravar como txt no mesmo dir
    if not output:
        if not input:
            # não há input nem output? Usar defaults da config
            input = default_input
            output = default_output
            if verbose:
                print 'Input:     ' % input
                print 'Output:    ' % output
        else:
            if os.path.isfile(input):
                # input é ficheiro, output é o mesmo mas com extensão .txt
                output = input.replace('.html', '.txt')
            else:
                # input é directório, output vai pra lá também
                output = input
    # só há output? Herp derp, vamos presumir que o input é o default
    if output and not input:
        input = default_input

    if os.path.isdir(input):
        import glob
        inputs = {}
        for f in glob.glob(os.path.join(input, '*.html')):
            if output:
                inputs[f] = os.path.join(output, os.path.basename(f).replace('.html', '.txt'))
            else:
                # sem output -> grava o txt no mesmo dir
                inputs[f] = os.path.join(input, os.path.basename(f).replace('.html', '.txt'))
        for i in inputs:
            if verbose: print '  %s -> %s' % (i, inputs[i])
            parse_file(i, inputs[i])
    else:
        parse_file(input, output)

