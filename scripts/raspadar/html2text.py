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

LOWERCASE_LETTERS = unicode(string.lowercase) + u'áàãâéèêíìóòõôúùç'

SUMMARY_STRINGS = ('SUMÁRIO', 'S U M Á R I O', 'SUMÁRI0', 'SUMARIO')
TITLES = ('Ex.mos Srs. ', 'Ex. mos Srs. ', 'Exmos Srs. ', 'Ex.. Srs. ', 'Ex.mos. Srs. '
          'Ex.mo Sr. ', 'Exmo. Sr. ', 'Ex.. Sr.', 'Ex.mo. Sr. ', 'Ex. mo Sr.', 'Ex. mos Srs.'
          )

MESES = {
    u'JANEIRO': 1,
    u'FEVEREIRO': 2,
    u'MARÇO': 3,
    u'ABRIL': 4,
    u'MAIO': 5,
    u'JUNHO': 6,
    u'JULHO': 7,
    u'AGOSTO': 8,
    u'SETEMBRO': 9,
    u'OUTUBRO': 10,
    u'NOVEMBRO': 11,
    u'DEZEMBRO': 12,
    }

NUMEROS_ROMANOS = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
    'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
    'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15,
    'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20,
    'XXI': 21, 'XXII': 22, 'XXIII': 23, 'XXIV': 24, 'XXV': 25,
    }

REPLACES_FILE = '/home/rlafuente/code/transparencia/datasets/transcricoes/replaces.txt'

REPLACES = [
        # o carácter 'é' às vezes é lido como 'ç', temos de substituir onde não bater certo
        # presumimos que se não for seguido por certas vogais, é erro de OCR
        (re.compile(ur'ç(?P<char>[^(aouãâáàóòõôúù)])', re.UNICODE), u'é\g<char>'),
        # o mesmo para o carácter 'ú', que é mal lido como 'õ'
        # se não for seguido de um e ('õe'), presumimos que é erro
        (re.compile(ur'õ(?P<char>[^(e)])', re.UNICODE), u'ú\g<char>'),
        # acrescentar espaços à frente da pontuação onde faltam
        # procura exemplos como ".Á", ",é" mas não ".R." (pode ser uma sigla)
        # no entanto omitimos ".a", por causa de "Sr.as"
        (re.compile(ur'(?P<pont>[.,?!])(?P<char>[A-Zb-zÁÀÉÍÓÚ][^\.])', re.UNICODE), u'\g<pont> \g<char>'),

        # newlines mal postas
        (re.compile(ur'(?P<titulo>Sr.|Sr.ª|Srs.)\n', re.UNICODE), '\g<titulo> '),

        # gralhas
        (re.compile(ur'CDSPP', re.UNICODE), 'CDS-PP'),
        (re.compile(ur'PrimeiroMinistro', re.UNICODE), 'Primeiro-Ministro'),
        (re.compile(ur'Primeiro Ministro', re.UNICODE), 'Primeiro-Ministro'),
        (re.compile(ur'deeuros', re.UNICODE), 'de euros'),
        (re.compile(ur'sms', re.UNICODE), 'SMS'),
        (re.compile(ur'Mubarack', re.UNICODE), 'Mubarak'),
        (re.compile(ur'Bourgiba', re.UNICODE), 'Bourguiba'),
        (re.compile(ur'Merkl', re.UNICODE), 'Merkel'),
        (re.compile(ur'háde', re.UNICODE), u'há de'),
        (re.compile(ur'digolhe', re.UNICODE), 'digo-lhe'),
        (re.compile(ur'peco-lhe', re.UNICODE), u'peço-lhe'),
        (re.compile(ur'dizerlhe', re.UNICODE), 'dizer-lhe'),
        (re.compile(ur'DecretoLei', re.UNICODE), 'Decreto-Lei'),
        # erros específicos de determinadas transcrições
        # XI legislatura
        (re.compile(ur'O S. Agostinho Lopes', re.UNICODE), 'O Sr. Agostinho Lopes'),
        (re.compile(ur'Deputado falou: - ', re.UNICODE), 'Deputado falou - '),
        (re.compile(ur'^Sr. Pedro Mota Soares', re.UNICODE), 'O Sr. Pedro Mota Soares'),
        (re.compile(ur'da Justiça. O Sr. Secretário de Estado', re.UNICODE), u'da Justiça.\n\nO Sr. Secretário de Estado'),
        (re.compile(ur'^O Secretário de Estado da Educação \(J', re.UNICODE), u'O Sr. Secretário de Estado da Educação (J'),
        (re.compile(ur'^O Sr. Ministros', re.UNICODE), u'O Sr. Ministro'),
        
    ]

### Regexes para detecção de erros de OCR ###

# nomes próprios portugueses
#re_nome = ur"[A-Zd][a-z\-ç'(é )]+\b|Álvaro"
re_nome = ur"[A-Zd][a-z\-']+|e"
re_n = re.compile(re_nome, re.UNICODE)

# data da sessão
re_data = (re.compile(ur'REUNIÃO( PLENÁRIA)? DE (?P<day>[0-9]{1,2}) DE (?P<month>[A-Za-zÇç]+) DE (?P<year>[0-9]{4})', re.UNICODE), '')


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
    elif type(item) in (str, unicode):
        s += item
    else:
        logging.warning('Unexpected object inside statements (%s)' % str(type(item)))
    return s

def strip_accents(s):
    import unicodedata
    if not type(s) == unicode:
        new_s = str(s)
        new_s = new_s.decode('UTF-8')
        new_s = ''.join((c for c in unicodedata.normalize('NFD', new_s) if unicodedata.category(c) != 'Mn'))
        return new_s.encode('UTF-8')
    else:
        s = re.sub(re.compile(ur'\xe1|\xe0|\xe2|\xe3', re.UNICODE), 'a', s)
        s = re.sub(re.compile(ur'\xe7', re.UNICODE), 'c', s)
        s = re.sub(re.compile(ur'\xe9|\xe8|\xea', re.UNICODE), 'e', s)
        s = re.sub(re.compile(ur'\xec|\xed', re.UNICODE), 'i', s)
        s = re.sub(re.compile(ur'\xf3|\xf2|\xf4|\xf5', re.UNICODE), 'o', s)
        s = re.sub(re.compile(ur'\xfa|\xf9', re.UNICODE), 'u', s)

        s = re.sub(re.compile(ur'\xc1|\xc0|\xc2|\xc3', re.UNICODE), 'A', s)
        s = re.sub(re.compile(ur'\xc7', re.UNICODE), 'C', s)
        s = re.sub(re.compile(ur'\xc9|\xc8|\xca', re.UNICODE), 'E', s)
        s = re.sub(re.compile(ur'\xcc|\xcd', re.UNICODE), 'I', s)
        s = re.sub(re.compile(ur'\xd2|\xd3|\xd4|\xd5', re.UNICODE), 'O', s)
        s = re.sub(re.compile(ur'\xda|\xd9', re.UNICODE), 'U', s)

        return s

def is_full_name(s):
    # Devolve True se a cadeia for um nome de pessoa
    s = s.strip('\n ')
    stripped_s = strip_accents(s)
    non_matches = re.split(re_n, stripped_s)

    for item in non_matches:
        if item.strip():
            return False
    return True
    
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
            #if started:
            paras = page.findAll('p')
            #else:
            #    paras = page.findAll('p')
            started = True

            t = u''
            if paras:
                if paras[0].contents:
                    header = paras[0].contents[0]
                    t += header
                    if type(header) == NavigableString:
                        if '|' in header or header.isupper() or u'NÚMERO' in header or u'SÉRIE' in header:
                            del paras[0]

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
                            elif el.name in ('sup', 'sub'):
                                text = el.contents[0].strip(' \n')
                                p += text
                            elif el.name in ('hr', 'u'):
                                # TODO: a hr deve quebrar o parágrafo e começar outro
                                pass
                            elif el.name == 'remove':
                                for c in el.contents:
                                    if type(c) == NavigableString:
                                        # text
                                        text = c.strip('\n').strip()
                                        text = text.replace('\n', ' ').strip()
                                        p += ' ' + text
                                    elif c.name == '\n':
                                        p += '\n'

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
                    pass    
                first = False

    def parse_paragraph(self, p, first=False, skip_encode=False):
        '''
        if skip_encode:
            text = p
        else:
            text = p.encode('utf-8')
        '''
        text = p.strip(' \n')

        text = self.correct_inconsistencies(text)

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


        # tentar remover newlines que não deviam lá estar

        # guardar duplas newlines, temos de as conservar com
        # um placeholder
        text = text.replace('\n\n', '#NNN#')

        lines = text.split('\n')
        new_lines = []
        for line in lines:
            if u'#Secretários: ' in line:
                new_lines.append(line.strip() + '\n')
                continue
            # tratar das newlines
            if (line.endswith(('.', '?', '!', ':')) and not line.endswith(('Sr.', 'Srs.', u'Srª.'))) or is_full_name(line.strip('\n ')):
                new_lines.append(line + '\n')
            else:
                new_lines.append(line + ' ')

        text = ''.join(new_lines).strip('\n')
        # repôr duplas newlines
        text = text.replace('#NNN#', '\n\n')

        lines = text.split('\n\n')
        for line in lines:
            idx = lines.index(line)
            if line.strip().startswith(('Presidente: ', u'Secretários: ')):
                for t in TITLES:
                    if t in line:
                        # retirar título
                        lines[idx] = line.replace(t, '')
                        # remover duplo espaçamento resultante
                        lines[idx] = lines[idx].replace('  ', ' ')
        text = '\n\n'.join(lines)

        if 'BREAK' in text:
            print text

        # separar parágrafos que têm duas newlines
        if '\n\n' in text:
            paras = text.split('\n\n')
            # pprint(paras)
            for p in paras:
                self.paragraphs.append(p)
        else:
            self.paragraphs.append(text)

    def correct_ocr(self):
        new_paras = []
        if not self.paragraphs:
            return
        while 1:
            if not self.paragraphs:
                break
            text = self.paragraphs[0]
            # aplicar regexes para alguns erros OCR
            # as regexes estão definidas no início deste ficheiro
            text = text.replace(u' ç ', u' é ')
            text = text.replace('&nbsp;', '')
            new_paras.append(text)
            self.paragraphs.pop(0)
        self.paragraphs = list(new_paras)

    def correct_inconsistencies(self, para):
        para = para.strip('\n ')
        # travessão errado
        para = para.replace(u'\u2014', '-')
        # inconsistência no espaço após o speaker
        para = para.replace(u'-  ', '- ')
        # reticências
        if para.endswith(u'»') and not u'«' in para:
            para = para.replace(u'»', u'…')
        if u'»' in para and not u'«' in para:
            para = para.replace(u'»', u'…')
        if para.startswith(u'»'):
            para = para.replace(u'»', u'…')
        if u': — »' in para:
            para = para.replace(u': — »', u': — …')
        para = para.replace(u'...', u'…')

        for regex, subst in REPLACES:
            # consultar substituições
            if re.search(regex, para):
                para = re.sub(regex, subst, para)

        return para

    def get_date(self):
        for p in self.paragraphs:
            if re.search(re_data[0], p):
                m = re.search(re_data[0], p)
                #print m
                #print m.groups()
                #print m.group('day')
                day = int(m.group('day'))
                month = MESES[m.group('month').upper()]
                year = int(m.group('year'))
                self.date = datetime.date(year, month, day)
            # if matches date RE
            # save the date, else raise error
        if not self.date:
            raise RuntimeError('Session date not found')
        return self.date

    def get_txt(self):
        output = ''
        for s in self.paragraphs:
            if not s.strip('\n '):
                continue
            else:
                output += s + '\n\n'

        return output

    def run(self, soup, get_date=True):
        '''Parse the BeautifulSoup instance. get_date enables us to skip
        date detection in unit tests.'''
        self.parse_soup(soup)
        if get_date:
            self.get_date()
        self.correct_ocr()

def parse_html_file(infile, outfile):
    f = infile
    html = open(f, 'r')
    soup = BeautifulSoup(html)
    parser = QDSoupParser()
    try:
        parser.run(soup)
    except:
        logging.error('Parsing error in file %s.' % (f))
        raise

    outfile = outfile.rsplit('.')[0] + '_' + str(parser.date) + '.' + outfile.rsplit('.')[1]
    import codecs
    out = codecs.open(outfile, 'w', 'utf-8')
    out.write(parser.get_txt())
    out.close()
    return outfile

if __name__ == '__main__':
    import sys
    from ConfigParser import SafeConfigParser

    # analisar o ficheiro config
    parser = SafeConfigParser()
    parser.read('raspadar.conf')
    default_input = os.path.abspath(parser.get('txt2taggedtext', 'sourcedir'))
    default_output = os.path.abspath(parser.get('txt2taggedtext', 'targetdir'))

    # analisar as opções da linha de comandos
    import optparse
    # print 'ARGV      :', sys.argv[1:]
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
    parser.add_option('-p', '--picky',
                      dest="picky",
                      default=False,
                      action="store_true",
                      help='Stop batch processing in case an error is found',
                      )
    parser.add_option('-f', '--force',
                      dest="force",
                      default=False,
                      action="store_true",
                      help='Process file even if the output file already exists',
                      )
    options, remainder = parser.parse_args()
    input = options.input
    verbose = options.verbose
    output = options.output
    picky = options.picky

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
                output = input.replace('.txt', '.tag.txt')
            else:
                # input é directório, output vai pra lá também
                output = input
    # só há output? Herp derp, vamos presumir que o input é o default
    if output and not input:
        input = default_input

    if os.path.isdir(input):
        successes = []
        failures = []
        import glob
        inputs = {}
        for f in glob.glob(os.path.join(input, '*.html')):
            if output:
                inputs[f] = os.path.join(output, os.path.basename(f).replace('.html', '.txt'))
            else:
                # sem output -> grava o txt no mesmo dir
                inputs[f] = os.path.join(input, os.path.basename(f).replace('.html', '.txt'))
        for i in inputs:
            if os.path.exists(inputs[i]) and not options.force:
                print 'File %s exists, not overwriting.' % inputs[i]
                continue
            if verbose: print '  %s -> %s' % (i, inputs[i])
            try:
                parse_html_file(i, inputs[i])
                successes.append(i)
            except:
                logfile = open('broken-txt2tag.log', 'a')
                logfile.write(i + '\n')
                logfile.close()
                if picky:
                    sys.exit()
                failures.append(i)
        if verbose:
            print '----------------------------------'
            print 'Successfully parsed:   %d files' % len(successes)
            print 'Failed:                %d files' % len(failures)
            print '----------------------------------'
                
    else:
        parse_html_file(input, output)

