#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import locale
locale.setlocale(locale.LC_ALL, 'pt_PT.UTF8')

import logging
logging.basicConfig(level=logging.DEBUG)

import os
import string
import datetime


from html2text import add_item

### Constantes ###

MP_STATEMENT = 'int-dep'
GOV_STATEMENT = 'int-gov'
PM_STATEMENT = 'int-pm'
PRESIDENT_STATEMENT = 'presidente'
STATEMENT = 'intervencao'
INTERRUPTION = 'interrupcao'
APPLAUSE = 'aplauso'
PROTEST = 'protesto'
LAUGHTER = 'riso'
NOTE = 'nota'
PAUSE = 'pausa'
VOTE = 'voto'
SECRETARY = 'int-sec'
OTHER = 'outro'

INTRO = 'intro'
SUMMARY = 'sumario'
ROLLCALL_PRESENT = 'chamada-presentes'
ROLLCALL_ABSENT = 'chamada-ausentes'
ROLLCALL_LATE = 'chamada-atrasados'

MP_START = 'mp-inicio'
MP_CONT = 'mp-cont'
MP_ASIDE = 'mp-aparte'
OTHER_START = 'outro-inicio'
OTHER_CONT = 'outro-cont'

PRESIDENT_NEWSPEAKER = 'presidente-temapalavra'
PRESIDENT_ROLLCALL = 'presidente-chamada'
PRESIDENT_SUSPEND = 'presidente-suspensa'
PRESIDENT_REOPEN = 'presidente-reaberta'

ORPHAN = 'orfao'

### Regexes ###

re_hora = r'Eram (?P<hours>[0-9]{1,2} horas e (?P<minutes>)[0-9]{1,2} minutos.)'
# Separador entre orador e intervenção (algumas gralhas e inconsistências obrigam-nos
# a ser relativamente permissivos ao definir a expressão)
# Importa notar que esta regex é unicode, por causa dos hífens (o Python não os vai
# encontrar de outra forma)
re_separador = (re.compile(ur'\:[ \.]?[\–\–\—\-]', re.LOCALE|re.UNICODE), ': -')

re_titulo = (re.compile(r'O Sr\.|A Sr\.(ª)?'), '')

re_president = (re.compile(r'O Sr\.|A Sr\.(ª)? Presidente\ ?(?P<nome>\([\w ]+\))?(?P<sep>\:[ \.]?[\–\–\—\-])'), '')

re_cont = (re.compile(ur'O Orador|A Oradora(?P<sep>\:[ \.]?[\–\–\—\-])', re.UNICODE), '')

re_interv = (re.compile(ur'^(?P<titulo>O Sr\.|A Sr\.(ª)?)\ ?(?P<nome>[\w ]+)\ ?(?P<partido>\([\w -]+\))?(?P<sep>\:[ \.]?[\–\–\—\-])', re.UNICODE), '')
# re_interv = (re.compile(ur'^(?P<titulo>O Sr\.|A Sr\.(ª)?)\ ?(?P<nome>[\w ]+)\ (?P<partido>\([\w ]+\))?(?P<sep>\:[ \.]?[\–\–\—\-])', re.UNICODE), '')


class RaspadarTagger:
    def __init__(self):
        self.contents = []

    def parse_txt_file(self, txtfile):
        buffer = open(txtfile, 'r').read()
        paragraphs = buffer.split('\n\n')
        for para in paragraphs:
            self.parse_paragraph(para)

    def parse_paragraph(self, p):
        p = p.decode('utf-8')
        if not p:
            return
        # corresponde à regex de intervenção?
        if re.search(re_interv[0], p):
            # é intervenção
            self.parse_statement(p)
        elif re.search(re_cont[0], p):
            # é a continuação de uma intervenção ("O Orador")
            self.parse_statement(p, cont=True)
        else:
            # é outra coisa
            self.parse_other(p)

    def parse_statement(self, p, cont=False):
        if cont:
            p = re.sub(re_cont[0], re_cont[1], p, 1).strip()
            output = '[%s] %s' % (MP_CONT, p)
        else:
            p = re.sub(re_titulo[0], re_titulo[1], p, 1).strip()
            if p.startswith('Presidente'):
                self.parse_president(p)
            # TODO: Regex para Secretári[oa]( \()|(:)
            if p.startswith('Secretári'):
                self.parse_president(p)
            else: 
                output = '[%s] %s' % (STATEMENT, p)
                self.contents.append(output)
                return output

    def parse_president(self, p):
        # extrair nome do/a presidente, caso lá esteja
        m = re.search(re_president[0], p)
        if m:
            name = m.group('nome')
        # retirar todo o nome e separador 
        p = re.sub(re_president[0], re_president[1], p, 1).strip()
        output = '[%s] %s' % (PRESIDENT_STATEMENT, p)
        # TODO: name -> speaker?
        self.contents.append(output)
        return output

    def parse_secretary(self, p):
        pass

    def parse_government(self, p):
        pass

    def parse_other(self, p):
        if p.startswith('Aplauso'):
            output = '[%s] %s' % (APPLAUSE, p)
        elif p.startswith('Protesto'):
            output = '[%s] %s' % (PROTEST, p)
        elif p.startswith('Riso'):
            output = '[%s] %s' % (LAUGHTER, p)
        elif p.startswith(('Vozes', 'Uma voz d')):
            output = '[%s] %s' % (INTERRUPTION, p)
        elif p.startswith((u'SUMÁR', u'S U M Á R')):
            output = '[%s] %s' % (SUMMARY, p)
        else:
            output = '[%s] %s' % (ORPHAN, p)
        self.contents.append(output)
        return output

    def get_txt(self):
        output = ''
        for s in self.contents:
            if not type(s) in (str, unicode):
                add_item(output, s)
            elif s:
                output += s.strip('\n ').encode('utf-8') + '\n\n'
        return output

def parse_file(infile, outfile):
    f = infile
    tagger = RaspadarTagger()
    try:
        tagger.parse_txt_file(infile)
    except:
        logging.error('Tagging error in file %s.' % (f))
        raise

    outfile = open(outfile, 'w')
    outfile.write(tagger.get_txt())
    outfile.close()

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
                output = input.replace('.txt', '.tag.txt')
            else:
                # input é directório, output vai pra lá também
                output = input
    # só há output? Herp derp, vamos presumir que o input é o default
    if output and not input:
        input = default_input

    if os.path.isdir(input):
        import glob
        inputs = {}
        for f in glob.glob(os.path.join(input, '*.txt')):
            if output:
                inputs[f] = os.path.join(output, os.path.basename(f).replace('.txt', '.tag.txt'))
            else:
                # sem output -> grava o txt no mesmo dir
                inputs[f] = os.path.join(input, os.path.basename(f).replace('.txt', '.tag.txt'))
        for i in inputs:
            if verbose: print '  %s -> %s' % (i, inputs[i])
            parse_file(i, inputs[i])
    else:
        parse_file(input, output)

