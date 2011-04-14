#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup, NavigableString
import os
import string
import datetime
import re
import logging
logging.basicConfig(level=logging.ERROR)
from pprint import pprint

LOWERCASE_LETTERS = string.lowercase + 'áàãâéèêíìóòõôúùç'

SOURCE_DIR = './html/'
TARGET_DIR = './txt/'

SUMMARY_STRINGS = ('SUMÁRIO', 'S U M Á R I O', 'SUMÁRI0')
TITLES = ('Secretários: ', 'Ex.mos Srs. ', 'Ex. mos Srs. ', 'Exmos Srs. ', 'Ex.. Srs. '
          'Presidente: ', 'Ex.mo Sr. ', 'Exmo. Sr. ', 'Ex.. Sr.', 
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


class QDSoupParser:
    def __init__(self):
        self.date = None
        self.summary = None
        self.start_time = None
        self.end_time = None
        self.president = None
        self.secretaries = []
        self.statements = []

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
        # usamos regexes porque existem vários erros de redacção, mas elas
        # têm problemas com Unicode, por isso não usamos o sub
        regex = re.compile(r'.*:[ .]?[-—] ?.*')
        regex_part = re.compile(r':[ .]?[-—] ?')
        if regex.match(text):
            text = text.replace('O Sr. ', '')
            text = text.replace('A Sr.ª ', '')
            text = text.replace(': -', ': -')
            text = text.replace(': –', ': -')
            text = text.replace(':.-', ': -')
            text = text.replace(': —', ': -')
            text = text.replace(':.—', ': -')
            text = text.replace(':—', ': -')
            text = text.replace(':-', ': -')
            if text.count(': -') == 1:
                stype = STATEMENT
                speaker, text = text.split(': -')
                text = text.strip(' ')

            elif text.count(': -') > 1:
                # Se encontrou vários separadores de intervenção, quer dizer
                # que está mal redigido, vamos lá resolver isto
                if text.find('\\n'):
                    logging.debug('Composite statement: Found newline.')
                    texts = text.rsplit('\\n')
                elif '\xe2\x80\xa6' in text: 
                    logging.debug('Composite statement: Found ellipsis.')
                    # ellipsis
                    texts = text.rsplit('\xe2\x80\xa6'.decode('utf-8'), 1)
                    #texts[0] += '\xe2\x80\xa6'.decode('utf-8')
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
                        #texts[0] += '\xe2\x80\xa6'.decode('utf-8')

                if not len(texts) > 1:
                    if '\xe2\x80\xa6' in text:
                        logging.error('Ellipsis found in unbroken text! Preposterous!')
                    logging.warning('Two statements in one line!')
                    # pprint(texts)
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

            if speaker.startswith('Presidente'):
                if '(' in speaker:
                    try:
                        party, speaker = speaker.split('(')
                    except ValueError:
                        print speaker
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

        if first and stype not in (STATEMENT, MP_STATEMENT):
            # first paragraph of the page can be a continuation of previous
            if text[0] in LOWERCASE_LETTERS:
                self.statements[-1] = self.statements[-1].strip()
                self.statements[-1] += text + '\n\n'
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

        # limpar statements órfãos
        if stype == STATEMENT and not party and not speaker and self.statements:
            if type(self.statements[-1]) == list:
                print self.statements[-1]
            if self.statements[-1].startswith('[mp]'):
                self.statements[-1] = self.statements[-1].strip()
                self.statements[-1] += text + '\n\n'
                return None
            elif self.statements[-1].startswith('**') and self.statements[-2].startswith('[mp]'):
                self.statements[-2] = self.statements[-2].strip()
                self.statements[-2] += text + '\n\n'
                return None

        if stype in (NOTE, PROTEST, APPLAUSE, LAUGHTER):
            s = '** %s **\n\n' % (text)
        else:
            text = text.replace(' ç ', ' é ')
            if speaker and not party:
                s = '[%s] %s: - %s\n\n' % (stype, speaker, text)
            elif party and not speaker:
                s = '[%s] (%s): - %s\n\n' % (stype, party, text)
            elif party and speaker:
                s = '[%s] %s (%s): - %s\n\n' % (stype, speaker, party, text)
            else:
                s = '[%s] - %s\n\n' % (stype, text)
        return s

    def parse_soup(self, soup):
        output = ''
        self.statements = []
        started = False
        for page in soup.findAll('body'):
            output += '\n===============================\n'
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
                            elif not el:
                                pass
                            else:
                                logging.warning('Unidentified paragraph element found in HTML.')
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

        self.clean_statements()
        self._extract_metadata()
        return self.statements

    def clean_statements(self):
        for s in self.statements:
            if type(s) == str:
                s = s.strip(' ')
                # FIXME: Isto não está a fazer a substituição como esperado!
                s = s.replace('&nbsp;', '')
            else:
                logging.warning('Non-string statement found (%s)' % str(type(s)))

    def _extract_metadata(self):
        i = None
        # pprint(self.statements[:10])
        
        for s in self.statements:
            if s and 'encerrou a sessão' in s:
                i = self.statements.index(s)
        # print i
        if not i:
            lines = self.statements[0].split('\\n\\n')
        else:
            lines = []
            all_lines = self.statements[:i+1]
            for item in all_lines:
                lines.extend(item.split('\\n\\n'))

        # pprint(lines)

        for line in lines:
            looking_for = ('REUNIÃO', 'PLENÁRIA')
            if line.startswith(looking_for):
                logging.info('QDParser: Session date found!')
                try:
                    # vamos apanhar a data
                    t = line.strip()
                    verbose_date = line.split(' ')[3:]
                    day = int(verbose_date[0])
                    month = MESES[verbose_date[2]]
                    year = int(verbose_date[4].strip())
                    self.date = datetime.date(year, month, day)
                except ValueError:
                    print line
                    raise


            elif line.startswith('Presidente:'):
                logging.info('QDParser: President found!')
                line = line.strip()
                name = remove_strings(line, TITLES)
                self.president = name

            elif line.startswith('Secretários: '):
                logging.info('QDParser: Secretaries found!')
                line_index = lines.index(line) 

                name = line.strip()
                name = remove_strings(name, TITLES)

                names = []

                if '\\n' in name.strip(): 
                    names = name.split('\n')
                else:
                    while name and not name.startswith(SUMMARY_STRINGS):
                        # print name
                        names.append(name)
                        line_index += 1
                        name = lines[line_index]
                self.secretaries = names
                if len(self.secretaries) == 1:
                    self.secretaries = self.secretaries[0].split('\\n')

            elif line.strip().startswith(SUMMARY_STRINGS):
                logging.info('QDParser: Summary found!')
                self.summary = ''
                l_index = lines.index(line) 
                for line in lines[l_index:]:
                    self.summary += line + '\n'
                # remove remainder
                self.summary = self.summary.split('&nbsp;')[0]
                self.summary = remove_strings(self.summary, SUMMARY_STRINGS).strip('\n')
                break
                
        if not self.president: logging.error('President not found') 
        if not self.date: logging.error('Session date not found') 
        if not self.secretaries: logging.error('Secretaries not found') 
        if not self.summary: logging.error('Summary not found') 

    def get_txt(self):
        output = ''
        for s in self.statements:
            if not type(s) == str:
                add_item(output, s)
            elif s:
                output += s

        return output


if __name__ == '__main__':
    import sys
    f = sys.argv[1]
    outfilename = os.path.join(TARGET_DIR, f.replace('.txt', '.csv'))
    filename, ext = os.path.splitext(outfilename)

    html = open(f, 'r')
    soup = BeautifulSoup(html)
    parser = QDSoupParser()

    try:
        parser.parse_soup(soup)
    except:
        print '  Parsing error in file %s.' % (f)
        raise

    if parser.date:
        filename += '_' + str(parser.date)
    else:
        print '  Session date not found.'
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
