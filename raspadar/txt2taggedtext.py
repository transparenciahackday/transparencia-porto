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
from pprint import pprint


from html2text import add_item

### Constantes ###

MP_STATEMENT = 'deputado_intervencao'
GOV_STATEMENT = 'governo_intervencao'
PM_STATEMENT = 'pm_intervencao'
MINISTER_STATEMENT = 'ministro_intervencao'
STATE_SECRETARY_STATEMENT = 'secestado_intervencao'
PRESIDENT_STATEMENT = 'presidente'
SECRETARY_STATEMENT = 'secretario'
STATEMENT = 'intervencao'

MP_INTERRUPTION = 'deputado_interrupcao'
INTERRUPTION = 'vozes_aparte'
APPLAUSE = 'aplauso'
PROTEST = 'protesto'
LAUGHTER = 'riso'
NOTE = 'nota'
PAUSE = 'pausa'
VOTE = 'voto'
TIME = 'hora'
OTHER = 'outro'

INTRO = 'intro'
SUMMARY = 'sumario'
ROLLCALL = 'chamada'
ROLLCALL_PRESENT = 'chamada_presentes'
ROLLCALL_ABSENT = 'chamada_ausentes'
ROLLCALL_LATE = 'chamada_atrasados'
ROLLCALL_MISSION = 'chamada_missao'
SECTION = 'seccao'
END = 'fim'

MP_START = 'mp_inicio'
MP_CONT = 'continuacao'
MP_ASIDE = 'deputado_aparte'
OTHER_START = 'outro_inicio'
OTHER_CONT = 'outro_cont'

PRESIDENT_ASIDE = 'presidente_aparte'
PRESIDENT_NEWSPEAKER = 'presidente_temapalavra'
PRESIDENT_ROLLCALL = 'presidente_chamada'
PRESIDENT_OPEN = 'presidente_aberta'
PRESIDENT_CLOSE = 'presidente_encerrada'
PRESIDENT_SUSPEND = 'presidente_suspensa'
PRESIDENT_REOPEN = 'presidente_reaberta'
PRESIDENT_SWITCH = 'presidente_troca'

ORPHAN = 'orfao'

### Regexes ###

re_hora = (re.compile(ur'^Eram (?P<hours>[0-9]{1,2}) horas e (?P<minutes>[0-9]{1,2}) minutos.$', re.UNICODE), '')
# Separador entre orador e intervenção (algumas gralhas e inconsistências obrigam-nos
# a ser relativamente permissivos ao definir a expressão)
# Importa notar que esta regex é unicode, por causa dos hífens (o Python não os vai
# encontrar de outra forma)
re_separador = (re.compile(ur'\:?[ \.]?[\–\–\—\-] ', re.LOCALE|re.UNICODE), ': -')
re_mauseparador = (re.compile(ur'(?P<prevchar>[\)a-z])\:[ \.][\–\–\—\-](?P<firstword>[\w\»])', re.LOCALE|re.UNICODE), '\g<prevchar>: - \g<firstword>')

re_titulo = (re.compile(ur'O Sr[\.:]|A Sr\.?(ª)?'), '')

re_ministro = (re.compile(ur'^Ministr'), '')
re_secestado = (re.compile(ur'^Secretári[oa] de Estado.*:'), '')

re_palavra = (re.compile(ur'(dou|tem|vou dar)(,?[\w ^,]+,?)? a palavra|faça favor[^ de terminar]', re.UNICODE|re.IGNORECASE), '')

re_concluir = (re.compile(ur'(tempo esgotou-se)|(esgotou-se o( seu)? tempo)|((tem (mesmo )?de|queira) (terminar|concluir))|((ultrapassou|esgotou|terminou)[\w ,]* o seu tempo)|((peço|solicito)(-lhe)? que (termine|conclua))|(atenção ao tempo)|(remate o seu pensamento)|(atenção para o tempo de que dispõe)|(peço desculpa mas quero inform)|(deixem ouvir o orador)|(faça favor de prosseguir a sua)|(poder prosseguir a sua intervenção)', re.UNICODE|re.IGNORECASE), '')

re_president = (re.compile(ur'O Sr\.?|A Sr\.?ª? Presidente\ ?(?P<nome>\([\w ]+\))?(?P<sep>\:[ \.]?[\–\–\—\-])'), '')

re_cont = (re.compile(ur'O Orador|A Oradora(?P<sep>\:[ \.]?[\–\–\—\-\-])', re.UNICODE), '')

re_voto = (re.compile(ur'^Submetid[oa]s? à votação', re.UNICODE), '')

re_interv = (re.compile(ur'^(?P<titulo>O Sr[\.:]?|A Sr[\.:]?(ª)?)\ (?P<nome>[\w ,’-]+)\ ?(?P<partido>\([\w -]+\))?(?P<sep>\:?[ \.]?[\–\–\—\-]? ?)', re.UNICODE), '')
re_interv_semquebra = (re.compile(ur'(?P<titulo>O Sr\.?|A Sr(\.)?(ª)?)\ (?P<nome>[\w ,’-]+)\ ?(?P<partido>\([\w -]+\))?(?P<sep>\:[ \.]?[\–\–\—\-])', re.UNICODE), '')

re_interv_simples = (re.compile(ur'^(?P<nome>[\w ,’-]+)\ ?(?P<partido>\([\w -]+\))?\ ?(?P<sep>\:?[ \.]?[\–\–\—\-]? )', re.UNICODE), '')

def change_type(p, newtype):
    stype, text = p.split(']', 1)
    text = text.strip()
    return '[%s] %s' % (newtype, text)

def get_type(p):
    stype, text = p.split(']', 1)
    stype = stype.strip('[] ')
    return stype

def get_speaker(p):
    stype, text = p.split(']', 1)
    text = text.strip()
    try:
        speaker, text = re.split(re_separador[0], text, 1)
    except ValueError:
        print 'Não consegui determinar o speaker. Vai vazio.'
        print '   ' + p
        print
        raise
        return ''
    return speaker

def get_text(p):
    stype, text = p.split(']', 1)
    text = text.strip()
    if ': -' in text:
        speaker, text = text.split(':', 1)
    else:
        pass
    return text

def strip_type(p):
    stype, text = p.split(']', 1)
    text = text.strip()
    return text

def check_and_split_para(p):
    # verificar se tem regex da intervenção
    # se não, return None
    # se sim, dividir e reagrupar
    pass

class RaspadarTagger:
    def __init__(self):
        self.contents = []
        # cache para registar cargos de governo e nomes
        self.gov_posts = {}

    def parse_txt_file(self, txtfile):
        buffer = open(txtfile, 'r').read()
        paragraphs = buffer.split('\n\n')
        for para in paragraphs:
            self.parse_paragraph(para)
        self.process_orphans()

    def parse_paragraph(self, p):
        p = p.decode('utf-8')
        p = p.strip(' \n')
        if not p:
            return
        # FIXME: monkeypatch aqui: É preciso rectificar os separadores. Isto devia
        # acontecer no html2txt, mas não tenho tempo agora para re-processar
        # os HTML's. Desculpem lá.
        if re.search(re_mauseparador[0], p):
            p = re.sub(re_mauseparador[0], re_mauseparador[1], p, count=1) 

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
            p = re.sub(re_cont[0], re_cont[1], p, 1)
            p = re.sub(re_separador[0], '', p, 1).strip()
            stype = MP_CONT
        else:
            if not (re.match(re_titulo[0], p) and re.search(re_separador[0], p)):
                stype = ORPHAN
            else:
                p = re.sub(re_titulo[0], re_titulo[1], p, count=1).strip(u'ª \n')
                if p.startswith('Presidente'):
                    return self.parse_president(p)
                elif re.match(re_ministro[0], p) or re.match(re_secestado[0], p):
                    return self.parse_government(p)
                elif p.startswith(u'Secretári') and not 'Estado' in re.split(re_separador[0], p)[0]:
                    return self.parse_secretary(p)
                elif re.match(re_interv_simples[0], p):
                    stype = MP_STATEMENT
                else: 
                    stype = STATEMENT

        output = '[%s] %s' % (stype, p)
        # encontrar intervenções onde não há quebra de linha
        # TODO: este check tem de ser feito no parse_paragraph
        if re.search(re_interv_semquebra[0], output):
            # print '### Encontrei uma condensada: ###'
            result = re.split(re_interv_semquebra[0], output)
            new_p = ''
            for part in result[1:]:
                if part and part != u'ª':
                    if part.endswith(('.', u'ª')):
                        new_p += part + ' '
                    else:
                        new_p += part
            # arrumar a primeira parte
            # print 'Primeira:  ' + result[0]
            # print 'Segunda:   ' + new_p
            # print
            self.contents.append(result[0])
            # processar a segunda
            try:
                self.parse_statement(new_p)
            except RuntimeError:
                # loop infinito, vamos mostrar o que se passa
                print 'Loop infinito ao processar uma linha com mais do que uma intervenção.'
                print u'1ª:   ' + result[0]
                print u'2ª:   ' + new_p
                sys.exit()
            return
        self.contents.append(output)
        return output

    def parse_president(self, p):
        # extrair nome do/a presidente, caso lá esteja
        m = re.search(re_president[0], p)
        if m:
            name = m.group('nome')
        # retirar todo o nome e separador 
        p = re.sub(re_president[0], re_president[1], p, 1).strip()
        if u'encerrada a sessão' in p or u'encerrada a reunião' in p:
            stype = PRESIDENT_CLOSE
        elif (u'quórum' in p or 'quorum' in p) and 'aberta' in p:
            stype = PRESIDENT_OPEN
        elif re.search(re_palavra[0], p):
            stype = PRESIDENT_NEWSPEAKER
        elif re.search(re_concluir[0], p):
            stype = PRESIDENT_ASIDE
        else:
            stype = PRESIDENT_STATEMENT

        output = '[%s] %s' % (stype, p)
        self.contents.append(output)
        return output

    def parse_government(self, p):
        # A linha vem assim
        #   Ministra da Saúde (Alice Nenhures): - Acho muito bem!
        # E nós queremos
        #   Alice Nenhures (Ministra da Saúde): - Acho muito bem!
        # E nas partes onde só é indicado o cargo, queremos re-incluir o nome
        # e para isso usamos o dicionário self.gov_posts como cache
        result = re.split(re_separador[0], p, 1)
        if len(result) == 2:
            speaker, text = result
        elif len(result) == 1:
            if re.search(re_separador[0], result[0]):
                # erros de redacção ex. 'Ministro do Trabalho: Blá blá blá'
                speaker, text = re.split(re.separador[0], result[0], 1)
            else:
                print '  Result too short'
                print result
        else:
            print '  Result too long'
            print result

        if '(' in speaker:
            post, speaker = speaker.strip(')').split('(')
            self.gov_posts[post.strip()] = speaker.strip()
            # pprint(self.gov_posts)
            # print
        else:
            # procurar o nome associado ao cargo que já registámos da primeira vez
            # que esta pessoa falou
            # print p
            post = speaker.strip()
            speaker = self.gov_posts[speaker.strip()].strip()
            # pprint(self.gov_posts)
            # print

        if post.startswith('Primeiro'):
            stype = PM_STATEMENT
        elif post.startswith('Ministr'):
            stype = MINISTER_STATEMENT
        elif post.startswith('Secret'):
            stype = STATE_SECRETARY_STATEMENT
        else:
            print post
            assert False

        output = '[%s] %s (%s): - %s' % (stype, speaker, post.strip(), text.strip())
        self.contents.append(output)
        return output

    def parse_secretary(self, p):
        #if 'Estado' in p[:p.find(':')]:
        #    return self.parse_government(p)
        #else:
        output = '[%s] %s' % (SECRETARY_STATEMENT, p)
        self.contents.append(output)
        return output

    def parse_other(self, p):
        # TODO: Era altamente fazer um tuple regex -> tipo, e aqui ter só um loopzinho
        # em vez deste esparguete todo
        if p.startswith('Aplauso'):
            output = '[%s] %s' % (APPLAUSE, p)
            stype = APPLAUSE
        elif p.startswith('Protesto'):
            stype = PROTEST
        elif p.startswith('Riso'):
            stype = LAUGHTER
        elif p.startswith(('Vozes', 'Uma voz d')):
            stype = INTERRUPTION
        elif p.startswith((u'SUMÁR', u'S U M Á R')):
            stype = SUMMARY
        elif re.match(re_hora[0], p):
            stype = TIME
        elif p.endswith('ORDEM DO DIA'):
            stype = SECTION
        elif p.startswith(('Entretanto, assumiu', 'Entretanto, reassumiu', 'Neste momento, assumiu', 'Neste momento, reassumiu')):
            stype = PRESIDENT_SWITCH
        elif re.match(re_voto[0], p):
            stype = VOTE
        elif p == 'Pausa.':
            stype = PAUSE
        elif (u'Série' in p and u'Número' in p) or \
              u'LEGISLATURA' in p or u'LEGISLATIVA' in p or \
              u'PLENÁRIA' in p or u'COMISSÃO' in p or u'DIÁRIO' in p:
            stype = INTRO
        elif p.startswith((u'Deputados presentes à', u'Srs. Deputados presentes à', u'Estavam presentes os seguintes')):
            stype = ROLLCALL_PRESENT
        elif (u'Deputados não presentes' in p and u'missões internacionais' in p):
            stype = ROLLCALL_MISSION
        elif u'Deputados que faltaram' in p or u'Faltaram à' in p:
            stype = ROLLCALL_ABSENT
        elif u'Deputados que entraram' in p:
            stype = ROLLCALL_LATE
        elif u'A DIVISÃO' in p:
            stype = END
        else:
            stype = ORPHAN

        output = '[%s] %s' % (stype, p)
        self.contents.append(output)
        return output

    def process_orphans(self):
        orphan_types = tuple(['[%s]' % t for t in (SUMMARY, ROLLCALL_PRESENT, ROLLCALL_ABSENT, ROLLCALL_LATE, ROLLCALL_MISSION)])

        for p in self.contents:
            if p.startswith(orphan_types):
                stype, remainder = p.split(' ', 1)
                stype = stype.strip('[]')
                # órfãos seguintes passam a ter o mesmo tipo
                new_p = self.contents[self.contents.index(p) + 1]
                if not new_p.startswith('[%s]' % ORPHAN):
                    continue
                self.contents[self.contents.index(p) + 1] = change_type(new_p, stype)

        new_contents = []
        while 1:
            p = self.contents[0]
            
            if len(self.contents) > 1:
                if get_type(self.contents[1]) == MP_CONT and get_type(p) == PRESIDENT_STATEMENT:
                    # declaração do presidente seguida de uma continuação - significa
                    # que a do presidente é um aparte
                    p = change_type(p, PRESIDENT_ASIDE)
                if new_contents:
                    prev_p = new_contents[-1]
                    if get_type(p) == ORPHAN and get_type(prev_p) == MP_STATEMENT:
                        p = change_type(p, MP_CONT)

            MAIN_INTERVENTION_TYPES = (MP_STATEMENT, MINISTER_STATEMENT, PM_STATEMENT, STATE_SECRETARY_STATEMENT, SECRETARY_STATEMENT) 

            if get_type(p) == PRESIDENT_NEWSPEAKER:
                next_p = self.contents[1]
                if get_type(next_p) in (LAUGHTER, APPLAUSE, PAUSE, INTERRUPTION):
                    for c in self.contents[1:]:
                        if get_type(c) in MAIN_INTERVENTION_TYPES:
                            next_p = self.contents[self.contents.index(c)]
                    # next_p = self.contents[2]
                elif not get_type(next_p) in MAIN_INTERVENTION_TYPES:
                    print 'A seguir a tem a palavra, não tenho o que esperava. É melhor conferir.'
                    print 'Tem a palavra:  %s' % p
                    print 'Seguinte:    :  %s' % next_p
                    raise TypeError

                speaker = get_speaker(next_p)
                lookahead = 2
                while 1:
                    try:
                        next_p = self.contents[lookahead]
                    except IndexError:
                        print 'Cheguei ao fim enquanto procurava órfãos de uma intervenção. Intervenção inicial:'
                        print p
                        break

                    if get_type(next_p) in (PRESIDENT_STATEMENT, PRESIDENT_NEWSPEAKER, PRESIDENT_CLOSE):
                        # intervenção do presidente = a anterior terminou
                        # print '  Acabou a intervenção:'
                        # print '    ' + p
                        # print '  Porque encontrei:'
                        # print '    ' + next_p
                        # print
                        break
                    elif get_type(next_p) in (MP_STATEMENT, MINISTER_STATEMENT, PM_STATEMENT, STATE_SECRETARY_STATEMENT):
                        if not speaker == get_speaker(next_p):
                            # outro deputado fala durante uma intervenção = aparte
                            self.contents[lookahead] = change_type(next_p, MP_ASIDE) 
                        else:
                            # mesmo deputado = continuação
                            self.contents[lookahead] = change_type(next_p, MP_CONT) 

                    elif get_type(next_p) in (MP_CONT, ORPHAN):
                        # continuação: adicionar orador original
                        # também partimos do princípio que órfãos no meio de intervenções = continuação
                        text = get_text(next_p)
                        new_text = '[%s] %s: - %s' % (MP_CONT, speaker, text)
                        self.contents[lookahead] = new_text
                    
                    lookahead += 1
            new_contents.append(self.contents.pop(0))
            if len(self.contents) == 0:
                break
        self.contents = list(new_contents)

        for p in self.contents:
            if get_type(p) == ORPHAN:
                if u'encerrada a sessão' in p:
                    self.contents[self.contents.index(p)] = change_type(p, PRESIDENT_CLOSE) 


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
        for f in glob.glob(os.path.join(input, '*.txt')):
            if output:
                inputs[f] = os.path.join(output, os.path.basename(f).replace('.txt', '.tag.txt'))
            else:
                # sem output -> grava o txt no mesmo dir
                inputs[f] = os.path.join(input, os.path.basename(f).replace('.txt', '.tag.txt'))
        for i in inputs:
            if os.path.exists(inputs[i]) and not options.force:
                print 'File %s exists, not overwriting.' % inputs[i]
                continue
            if verbose: print '  %s -> %s' % (i, inputs[i])
            try:
                parse_file(i, inputs[i])
                successes.append(i)
            except:
                outfile = open(inputs[i], 'w')
                outfile.close()
                if picky:
                    sys.exit()
                failures.append(i)
        if verbose:
            totalcount = len(successes) + len(failures)
            print '----------------------------------'
            print 'Successfully parsed:   %d files (%f%%)' % (len(successes), int(len(successes)/totalcount))
            print 'Failed:                %d files (%f%%)' % (len(failures), int(len(failures)/totalcount))
            print '----------------------------------'
                
    else:
        parse_file(input, output)

