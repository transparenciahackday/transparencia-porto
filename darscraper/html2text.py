#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(level=logging.DEBUG)

from BeautifulSoup import BeautifulSoup, NavigableString
import os
import string
import datetime
import re
import string

import locale
locale.setlocale(locale.LC_ALL, 'pt_PT.UTF8')

from pprint import pprint

LOWERCASE_LETTERS = string.lowercase + 'áàãâéèêíìóòõôúùç'

SOURCE_DIR = './html/'
TARGET_DIR = './txt/'

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

# Regexes para detecção de erros de OCR

# o carácter 'é' às vezes é lido como 'ç', temos de substituir onde não bater certo
# presumimos que se não for seguido por vogal, é erro de OCR
re_cedilha = r'ç(?P<char>[^(aeiouãâáàéèêíìóòõôúù)])'
# o mesmo para o carácter 'ú', que é mal lido como 'õ'
# se não for seguido de um e ('õe'), presumimos que é erro
re_otil = r'õ(?P<char>[^(e)])'
# acrescentar espaços à frente da pontuação onde faltam
# procura exemplos como ".Á", ",é" mas não ".R." (pode ser uma sigla)
# no entanto omitimos ".a", por causa de "Sr.as"
re_pontuacao = r'(?P<pont>[.,?!])(?P<char>[A-Zb-zÁÀÉÍÓÚ][^.])'
# nomes próprios portugueses
re_nome = r" ?[A-ZdÁ][a-z\-ç'(é )]+\b|Álvaro"

re_c = re.compile(re_cedilha, re.LOCALE|re.UNICODE|re.MULTILINE)
re_ot = re.compile(re_otil, re.LOCALE|re.UNICODE|re.MULTILINE)
re_pont = re.compile(re_pontuacao, re.LOCALE|re.UNICODE|re.MULTILINE)
re_n = re.compile(re_nome, re.LOCALE|re.UNICODE|re.MULTILINE)

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
    

class QDSoupParser:
    def __init__(self):
        self.date = None
        self.summary = None
        self.start_time = None
        self.end_time = None
        self.president = None
        self.secretaries = []
        self.statements = []

    def parse_soup(self, soup):
        output = ''
        self.statements = []
        started = False
        for page in soup.findAll('body'):
            # exclude the first paragraph, but not in the first page
            first = True
            if started:
                paras = page.findAll('p')[1:]
            else:
                paras = page.findAll('p')
                started = True

            for para in paras:
                if para.contents:
                    if len(para.contents) > 1:
                        p = ''
                        for el in para.contents:
                            if type(el) == NavigableString:
                                # text
                                text = el.strip('\n').strip()
                                text = text.replace('\n', ' ')
                                p += text
                            elif el.name == 'br':
                                # line break
                                p += '\\n'
                            elif el.name == 'sup':
                                text = el.contents[0].strip(' \n')
                                p += text
                            elif not el:
                                pass
                            else:
                                logging.warning('Unidentified paragraph element found in HTML.')
                                logging.warning('-> %s' % el)
                        st = self.parse_paragraph(p, first=first)
                        if st:
                            if type(st) == list:
                                for s in st:
                                    self.statements.append(s)
                            else:
                                self.statements.append(st)

                    else:
                        el = para.contents[0]
                        p = el.strip('\n').strip()
                        p = p.replace('\n', ' ')
                        st = self.parse_paragraph(p, first=first)
                        if st:
                            if type(st) == list:
                                for s in st:
                                    self.statements.append(s)
                            else:
                                self.statements.append(st)
                else:
                    assert False
                first = False

        return self.statements

    def parse_paragraph(self, p, first=False, skip_encode=False):
        if skip_encode:
            text = p
        else:
            text = p.encode('utf-8')

        speaker = ''
        party = ''
        stype = ''

        if not text:
            return

        # vamos procurar pelo conjunto de dois pontos e travessão, que
        # é o que indica uma intervenção

        # regex_part = re.compile(r':[ .]?[-—] ?')
        if re_interv.match(text):
            # TODO: o comando comentado devia substituir todos os replaces a seguir, mas por alguma
            # razão não está a dar, por isso de momento caguei neste problema
            # re.sub(re_interv, ': -', text)
            text = text.replace(': -', ': -')
            text = text.replace(': –', ': -')
            text = text.replace(':.-', ': -')
            text = text.replace(': —', ': -')
            text = text.replace(':.—', ': -')
            text = text.replace(':—', ': -')
            text = text.replace(':-', ': -')
            if text.count(': -') == 1:
                text = text.replace('O Sr. ', '', 1)
                text = text.replace('A Sr.ª ', '', 1)
                stype = STATEMENT
                speaker, text = text.split(': -')
                text = text.strip(' ')

            elif text.count(': -') > 1:
                # Se encontrou vários separadores de intervenção, quer dizer
                # que está mal redigido, vamos lá resolver isto
                logging.debug('** Two markers: %s' % text)
                if '… O Sr.' in text or '… A Sr.' in text:
                    logging.debug('Composite statement: Found possible second entry without opening newline.')
                    texts = text.rsplit('…') 
                    texts[0] += '…' 
                elif text.find('\\n\\n'):
                    logging.debug('Composite statement: Found double newline.')
                    texts = text.rsplit('\\n\\n')
                elif text.find('\\n'):
                    logging.debug('Composite statement: Found newline.')
                    texts = text.rsplit('\\n')
                elif '\xe2\x80\xa6' in text: 
                    logging.debug('Composite statement: Found ellipsis.')
                    # ellipsis
                    texts = text.rsplit('\xe2\x80\xa6'.decode('utf-8'), 1)
                elif '  ' in text:
                    logging.info('Composite statement: Found double space.')
                    texts = text.split('  ')
                else:
                    logging.error('No markers found in composite statement.')

                if not len(texts) > 1:
                    if '\xe2\x80\xa6' in text: 
                        logging.debug('Composite statement: Found ellipsis in second run.')
                        # ellipsis
                        texts = text.rsplit('\xe2\x80\xa6', 1)

                if not len(texts) > 1:
                    if '\\n\\n' in text:
                        texts = text.rsplit('\\n\\n')
                    elif '\xe2\x80\xa6' in text:
                        logging.error('Ellipsis found in unbroken text! Preposterous!')
                    
                    logging.warning('Two statements in one line!')
                else:
                    sts = []
                    for t in texts:
                        p = self.parse_paragraph(t, skip_encode=True)
                        if p:
                            sts.append(p)
                    return sts
            else:
                speaker = ''
                party = ''
                text = text.strip()

            if speaker.startswith('Presidente') or party is 'Presidente':
                if '(' in speaker:
                    try:
                        party, speaker = speaker.split('(')
                    except ValueError:
                        #print speaker
                        raise
                    speaker = speaker.strip(')')
                    party = party.strip()
                else:
                    speaker = 'Presidente'
                    party = 'Presidente'
                stype = PRESIDENT_STATEMENT

            elif 'Secretári' in speaker and not 'Estado' in speaker:
                if '(' in speaker:
                    post, name = speaker.split('(')
                    name = name.strip(')')
                    speaker = name
                    party = 'Secretário'
                    stype = SECRETARY

            elif 'Vozes' in speaker:
                stype = INTERRUPTION

            else:
                stype = STATEMENT

                if speaker.count('(') == 1:
                    try:
                        speaker, party = speaker.split('(')
                    except ValueError:
                        # print speaker
                        if len(speaker) > 200:
                            logging.error('Speaker too long, this is often a very bad sign.')
                            speaker = ''
                            party = ''
                        raise
                    speaker = speaker.strip()
                    party = party.strip(')')
                    stype = MP_STATEMENT
                else:
                    if speaker.count('(') > 1 and len(speaker) < 40:
                        logging.error('Too many parenthesis inside speaker.')
            if speaker.startswith('Ministr') or (speaker.startswith('Secret') and 'Estado' not in speaker):
                stype = GOV_STATEMENT
            if speaker.startswith('Primeiro'):
                speaker = 'Primeiro-Ministro'
                party = ''
                stype = PM_STATEMENT
        else:
            # Não é uma intervenção (não tem ': -'))
            if text.startswith('Aplausos'):
                stype = APPLAUSE
            elif text.startswith('Protestos'):
                stype = PROTEST
            elif text.startswith('Risos'):
                stype = LAUGHTER
            elif text.startswith('Pausa'):
                stype = PAUSE
            elif text.startswith('Submetid'):
                stype = VOTE
            elif 'assumiu a presidência' in text or text.startswith('Eram ') \
                    or text.startswith('Pausa.'):
                stype = NOTE

            else:
                stype = STATEMENT

        if first and stype not in (MP_STATEMENT,):
            # first paragraph of the page can be a continuation of previous
            if self.statements:
                if type(self.statements[-1]) == str:
                    if self.statements[-1].strip()[-1] not in '?!.':
                        self.statements[-1] = self.statements[-1].strip()
                        if text[0].startswith(tuple(string.uppercase)):
                            logging.debug('Concatenating with added newline. Check if this is OK.')
                            self.statements[-1] += '\\n' + text + '\\n\n'
                        else:
                            # print text[:20]
                            self.statements[-1] += text + '\\n\\n'
                        return None
                # FIXME: Check para listas, isto pode dar merda
                elif type(self.statements[-1]) == list:
                    if self.statements[-1][-1].strip()[-1] not in '?!.':
                        # print text[:20]
                        self.statements[-1][-1] = self.statements[-1][-1].strip()
                        self.statements[-1][-1] += text + '\n\n'
                        return None

            else:
                pass
        else:
            #if self.statements and not self.statements[-1].is_interruption():
            #if self.statements and self.statements[-1]:
            #    self.statements[-1] += ' ' + text
            #    return None
            #else:
            #    stype = OTHER
            pass

        # normalizar newlines
        if '\n\n' not in text:
            sentences = text.split('\\n')
            for s in sentences:
                # se acabar com ponto (e não uma abreviatura) e não for a última, acrescentar newline
                if s.endswith(('.', '!', '?')) and not s.endswith(('Srs.', 'O Sr.')) and not sentences.index(s) > len(sentences):
                    sentences[sentences.index(s)] += '\\n'
            text = " ".join(sentences)
            # retirar espaços a seguir às newlines
            text = text.replace('\\n ', '\\n')
            text = text.strip('\\n')

        # limpar statements órfãos
        if stype == STATEMENT and not party and not speaker and self.statements:
            if type(self.statements[-1]) == list:
                # print self.statements[-1]
                logging.warning('List found inside statements while looking for orphans.')
                pass
            if self.statements[-1].startswith('[mp]'):
                self.statements[-1] = self.statements[-1].strip()
                self.statements[-1] += text + '\n\n'
                return None
            #elif self.statements[-1].startswith('**') and self.statements[-2].startswith('[mp]'):
            #    self.statements[-2] = self.statements[-2].strip()
            #    self.statements[-2] += text + '\n\n'
            #    return None

        # limpar caracteres defeituosos (erros OCR)
        if '«' not in text:
            text = text.replace('»', '…')
        if text.startswith('»'):
            text = '…' + text.strip('»')
        if text.endswith('»'):
            text = text.strip('»') + '…' 

        text = text.replace(' ç ', ' é ')

        # aplicar regexes para alguns erros OCR
        # as regexes estão definidas no início deste ficheiro
        text = re.sub(re_c, 'é\g<char>', text)
        text = re.sub(re_ot, 'ú\g<char>', text)
        text = re.sub(re_pontuacao, '\g<pont> \g<char>', text)

        # terminado
        if stype in (NOTE, PROTEST, APPLAUSE, LAUGHTER):
            s = '** %s **\n\n' % (text)
        elif text == '&nbsp;':
            return None
        else:
            if speaker and not party:
                s = '[%s] %s: - %s\n\n' % (stype, speaker, text)
            elif party and not speaker:
                s = '[%s] (%s): - %s\n\n' % (stype, party, text)
            elif party and speaker:
                if party == speaker:
                    s = '[%s] %s: - %s\n\n' % (stype, speaker, text)
                else:
                    s = '[%s] %s (%s): - %s\n\n' % (stype, speaker, party, text)
            else:
                s = '[%s] - %s\n\n' % (stype, text)
        return s

    def clean_statements(self):
        cleaned_statements = []
        for s in self.statements:
            if type(s) == list:
                for item in s:
                    if type(item) == list:
                        for subitem in item:
                            cleaned_statements.append(subitem)
                    else:
                        cleaned_statements.append(item)
            elif type(s) == str:
                cleaned_statements.append(s)
            else:
                logging.warning('Non-string, non-list statement found (%s)' % str(type(s)))
        self.statements = cleaned_statements
        
        for s in self.statements:
            index = self.statements.index(s)
            prev_s = self.statements[index-1] if index else ''
            # print 'Statement: %s' % s.strip()
            # print 'Previous:  %s' % prev_s.strip()

            if type(prev_s) == list:
                print 'LIST FOUND'
                print s

            s = s.strip(' ')
            # FIXME: Isto não está a fazer a substituição como esperado!
            s = s.replace('&nbsp;', '')

            if prev_s.endswith('\n\n') and '**' not in prev_s and s.startswith('[statement]'):
                # logging.debug('Found double newline, joining with previous.')
                # frase incompleta, juntar à anterior
                if prev_s.strip('\n ')[-1] in LOWERCASE_LETTERS or prev_s.strip('\n ').endswith(('Sr.','Sra.','Srs.', 'Sras.', '—')):
                    self.statements[index-1] = self.statements[index-1].strip('\n') + ' '
                else:
                    self.statements[index-1] = self.statements[index-1].strip('\n') + '\\n'
                self.statements[index-1] += s.replace('[statement] - ', '')
                self.statements.pop(index)
            else:
                s = s.strip('\n ')

            # elif prev_s.endswith(LOWERCASE_LETTERS + '\n') and s.startswith('[statement]'):
            #     print 'INCOMPLETE 2' 
            #     # frase incompleta, juntar à anterior
            #     if prev_s.strip('\n ')[-1] not in LOWERCASE_LETTERS:
            #         prev_s = prev_s.strip('\n')
            #     prev_s += s.replace('[statement] - ', '')
            #     self.statements.pop(self.statements.index(s))


    def _trim_ending(self):
        # a transcrição acaba quando o presidente encerra a sessão
        # TODO: analisar declarações de voto e outras infos mencionadas
        # após o encerramento
        i = 0
        for s in reversed(self.statements):
           if s and ('encerrou a sessão' in s or 'encerrada a sessão' in s):
               if '\\n' in s:
                   lines = s.split('\\n')
                   for line in lines:
                       if 'encerrada a sessão' in line or 'encerrou a sessão' in line:
                           orig_s = s
                           lineindex = lines.index(line)
                           lines = lines[:lineindex+1]
                           s = '\\n'.join(lines)
                           self.statements[self.statements.index(orig_s)] = s + '\n\n'
                           break
               else:
                   i = self.statements.index(s)
                   print 'End index: %d' % i
                   self.statements = self.statements[:i+1]
                   break

            
    def _extract_metadata(self):
        i = None
        # pprint(self.statements[:10])
        
        first_statement = self.statements.pop(0)

        first_real_statement = self.statements.pop(0)

        while not first_real_statement.startswith(('[president]','[mp]')):
            first_statement += first_real_statement
            first_real_statement = self.statements.pop(0)

        last_statement = self.statements[-1]

        introlines = first_statement.split('\\n')

        # print first_real_statement
        # print string.count(first_real_statement, '\\n')

        opening_statements = []
        orphan_statements_in_intro = False
       
        for l in introlines:
            if 'temos qu' in l:
                orphan_statements_in_intro = True
                index = introlines.index(l)
                opening_statements = introlines[index:]
                introlines = introlines[:index]
                break
        if not opening_statements:
            if 'temos qu' in first_real_statement:
                opening_statements = first_real_statement.split('\\n')
            else:
                raise ValueError('Could not split first statement from introlines. Check for quorum line.')

        # print self.statements[:5]

        # processar opening_statements e remover linhas de chamada!
        items_to_remove = []
        for line in opening_statements:
            # procurar e remover nomes próprios e partidos
            if line.endswith('):') or (line.startswith(('Partido', 'Bloco')) and line.endswith(')')) or is_full_name(line):
                items_to_remove.append(line)
            if line.startswith('\n'):
                opening_statements[opening_statements.index(line)] = line.strip('\n') + '\n\n'
        for line in items_to_remove:
            try:
                opening_statements.remove(line)
            except ValueError:
                if line.strip('\n '):
                    # print line
                    raise

        # determinar hora de início
        for line in opening_statements:
            if line.strip().startswith('Eram') and 'horas' in line:
                opening_statements.remove(line)
                break

        # retirar linha dos deputados presentes
        for line in opening_statements:
            if 'Deputados presentes' in line:
                opening_statements.remove(line)
                break


        # pprint(opening_statements)

        lines_to_remove = []
        for line in opening_statements:
            prev_line = opening_statements[opening_statements.index(line)]
            if line.strip('\n ') and not line.startswith('[') and not line == '\\n':
                if not prev_line.startswith('[president]'):
                    opening_statements[opening_statements.index(line)] = '[president] ' + line + '\n\n'
                else:
                    prev_line += '\n%s' % line
                    line = ''
            elif not line.strip('\n ') or line == '\\n':
                lines_to_remove.append(line)
        for line in lines_to_remove:
            opening_statements.remove(line)


        if orphan_statements_in_intro:
            self.statements.insert(0, first_real_statement)
            for s in reversed(opening_statements):
                # TODO: ver se a linha tem tag!
                self.statements.insert(0, s)
        else:
            self.statements.pop(0)
            self.statements.insert(0, ''.join(opening_statements))



    
        # print first_real_statement
        # if not first_real_statement.startswith('[president]'):
        #     pres_line_index = 0
        #     for line in introlines:
        #         # print line.strip(' ')
        #         # print
        #         if (line.strip(' ').startswith('O Sr. Pres') and not 'encerrou' in line and not 'declarou' in line) or line.startswith('[president]'):
        #             pres_line_index = introlines.index(line)
        #             break
        #     if pres_line_index:
        #         beginning_statements = introlines[pres_line_index:]
        #         introlines = introlines[:pres_line_index]
        #     else:
        #         raise TypeError('No president first statement found')
        # 
        #     print '--- BEGINNING STATEMENTS ---'
        #     pprint(beginning_statements)
        #     print '--- INTRO ---'
        #     pprint(introlines)

        #     i = 0

        #     for s in beginning_statements:
        #         self.statements.insert(i, s)
        #         i += 1

        #     first_real_statement = self.statements[0]



        lines = introlines

        intro = lines[0].split('  ')
        summary_index = lines[0].find('SUM')
        if not summary_index:
            summary_index = lines[0].find('S U M')
        if not summary_index:
            logging.critical('Summary index not found!!')

        # TODO: Apanhar final do sumário!!
        lines[0] = lines[0][summary_index:]
        self.summary = '\\n'.join(lines)

        '''
        print
        print '--- INTRO ---'
        pprint(intro)
        print
        print '--- SUMMARY ---'
        pprint(lines)
        print
        '''
        # else:
        #    lines = []
        #    all_lines = self.statements[:i+1]
        #    for item in all_lines:
        #        lines.extend(item.split('\\n\\n'))


        for line in intro:
            orig_line = str(line)
            line = line.replace('[statement] - ', '').strip()
            looking_for = ('REUNIÃO', 'REUNIAO', 'PLENÁRIA')
            if line.startswith(looking_for):
                logging.info('QDParser: Session date found!')
                try:
                    # vamos apanhar a data
                    t = line.strip()
                    verbose_date = line.split(' ')[3:]
                    day = int(verbose_date[0])
                    month = MESES[verbose_date[2].upper()]
                    year = int(verbose_date[4].strip())
                    self.date = datetime.date(year, month, day)
                except ValueError:
                    # print line
                    raise

            elif line.startswith('Presidente:'):
                if 'Secret' in line:
                    # info presidente e secretários no mesmo parágrafo, derp
                    # print
                    logging.info('QDParser: President found!')
                    logging.info('QDParser: Secretaries found!')
                    line = line.strip()
                    names = remove_strings(line, TITLES)
                    names = names.split('\\n')
                    pres = names.pop(0)
                    self.president = pres.replace('Presidente: ', '')
                    # print self.president
                    secs = names
                    secs[0] = secs[0].replace('Ex.mos. Srs. ', '')
                    self.secretaries = secs

                    # print self.secretaries
                else:
                    logging.info('QDParser: President found!')
                    line = line.strip()
                    name = remove_strings(line, TITLES)
                    self.president = name

            elif line.startswith('Secretários: '):
                logging.info('QDParser: Secretaries found!')
                line_index = intro.index(orig_line) 

                name = line.strip()
                name = remove_strings(name, TITLES)

                names = []

                if '\\n' in name.strip(): 
                    names = name.split('\n')
                else:
                    while name and not name.startswith(SUMMARY_STRINGS):
                        # print name
                        # print line_index
                        names.append(name)
                        line_index += 1
                        name = intro[line_index]
                self.secretaries = names
                if len(self.secretaries) == 1:
                    self.secretaries = self.secretaries[0].split('\\n')

            '''
            elif line.strip().startswith(SUMMARY_STRINGS):
                logging.info('QDParser: Summary found!')
                self.summary = ''
                l_index = intro.index(orig_line) 
                for line in intro[l_index:]:
                    self.summary += line + '\n'
                # remove remainder
                self.summary = self.summary.split('&nbsp;')[0]
                self.summary = remove_strings(self.summary, SUMMARY_STRINGS).strip('\n')
                break
            '''
                
        if not self.president: logging.error('President not found') 
        if not self.date: logging.error('Session date not found') 
        if not self.secretaries: logging.error('Secretaries not found') 
        if not self.summary: logging.error('Summary not found') 

        self._trim_ending()

    def get_txt(self):
        output = ''
        for s in self.statements:
            if not type(s) == str:
                add_item(output, s)
            elif s:
                output += s

        return output

    def run(self, soup):
        self.parse_soup(soup)
        self.clean_statements()
        self.clean_statements()
        self.clean_statements()
        self._extract_metadata()

if __name__ == '__main__':
    import sys
    f = sys.argv[1]
    outfilename = os.path.join(TARGET_DIR, f.replace('.txt', '.csv'))
    filename, ext = os.path.splitext(outfilename)

    html = open(f, 'r')
    soup = BeautifulSoup(html)
    parser = QDSoupParser()

    try:
        parser.run(soup)
    except:
        logging.error('Parsing error in file %s.' % (f))
        raise

    if parser.date:
        filename += '_' + str(parser.date)
    else:
        logging.error('Session date not found.')
        # sys.exit()

        ext = '.txt'
    outfilename = filename + ext.replace('html', 'txt')
    outfile = open(outfilename, 'w')

    s1 = 'Data: %s\n' % str(parser.date)
    s2 = 'Presidente: %s\n' % str(parser.president)
    s3 = 'Secretários: %s\n' % ", ".join(parser.secretaries)
    outfile.write(s1)
    outfile.write(s2)
    outfile.write(s3)
    outfile.write('\n--------------\n\n')
    outfile.write(parser.get_txt())
    outfile.close()
    '''
    for f in os.listdir(SOURCE_DIR):
        print f
        if os.path.splitext(f)[1] != '.txt':
            print 'Not a text file, skipping.'

        outfilename = os.path.join(TARGET_DIR, f.replace('.txt', '.csv'))
        filename, ext = os.path.splitext(outfilename)

        exists = False
        for fn in os.listdir(TARGET_DIR):
            if filename.split('/')[-1] in fn:
                exists = True
                print 'Target file already exists, skipping.'
                break
        if exists:
            continue
                
        html = open(os.path.join(SOURCE_DIR, f), 'r')
        soup = BeautifulSoup(html)
        
        parser = QDSoupParser()
        try:
            parser.parse_soup(soup)
        except:
            print '  Parsing error in file %s.' % (f)
            raise
        processor = QDPostProcessor(parser)
        try:
            session = processor.run()
        except:
            logging.exception('Processing error in file %s.' % (f))
            continue

        if session.date:
            filename += '_' + str(session.date)
            outfilename = filename + ext
        else:
            print '  Session date not found. Not saving.'
            continue
        outfile = open(outfilename, 'w')
        outfile.write(session.get_statements_csv())
        outfile.close()
        """
        print 'Empty statement found. Not saving.'
        outfile.close()
        os.remove(outfilename)
        break
        """
     '''
