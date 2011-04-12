#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup, NavigableString
import os
import string
import datetime
import re
import logging
logging.basicConfig(level=logging.DEBUG)
from pprint import pprint

LOWERCASE_LETTERS = string.lowercase + 'áàãâéèêíìóòõôúùç'

SOURCE_DIR = './html/'
TARGET_DIR = './txt/'

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
PRESIDENT_STATEMENT = 'president'
STATEMENT = 'statement'
INTERRUPTION = 'interruption'
APPLAUSE = 'applause'
PROTEST = 'protest'
LAUGHTER = 'laughter'
NOTE = 'note'
OTHER = 'other'


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
            return None

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
            text = text.replace(':.-', ': -')
            text = text.replace(': —', ': -')
            text = text.replace(':.—', ': -')
            text = text.replace(':—', ': -')
            text = text.replace(':-', ': -')
            if text.count(': -') == 1:
                speaker, text = text.split(': -')
                text = text.strip(' ')

            elif text.count(': -') > 1:
                # Se encontrou vários separadores de intervenção, quer dizer
                # que está mal redigido, vamos lá resolver isto
                if text.find('\\n'):
                    logging.debug('Composite statement: Found newline.')
                    texts = text.split('\\n')
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
                    logging.error('Two statements in one line. Printing offending statement.')
                    pprint(texts)
                else:
                    sts = []
                    for t in texts:
                       sts.append(self.parse_paragraph(t, skip_encode=True))
                    return sts
            else:
                print text
                raise ValueError

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
                    
            else:
                if speaker in ('O Orador', 'A Oradora') and len(self.statements) > 1:
                    # get previous speaker
                    stype = MP_STATEMENT
                    # if self.statements[-2]:
                    #     speaker = self.statements[-2].speaker
                    #     party = self.statements[-2].party
                    # elif self.statements[-3]:
                    #     speaker = self.statements[-3].speaker
                    #     party = self.statements[-3].party
                    # elif self.statements[-4]:
                    #     speaker = self.statements[-4].speaker
                    #     party = self.statements[-4].party
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
                            print '  Speaker too long, this is often a very bad sign.'
                            speaker = ''
                            party = ''
                        raise
                    speaker = speaker.strip()
                    party = party.strip(')')
                    stype = MP_STATEMENT
                else:
                    if speaker.count('(') > 1:
                        logging.error('Too many parenthesis inside speaker.')
        else:
            if text.startswith('Aplausos'):
                stype = APPLAUSE
            elif text.startswith('Protestos'):
                stype = PROTEST
            elif text.startswith('Risos'):
                stype = LAUGHTER
            elif 'assumiu a presidência' in text or text.startswith('Eram ') \
                    or text.startswith('Pausa.'):
                stype = NOTE
            else:
                if first:
                    # first paragraph of the page can be a continuation of previous
                    if text[0] in LOWERCASE_LETTERS + ' ':
                        if self.statements:
                            self.statements[-1] += text
                            return None
                    else:
                        #if self.statements and not self.statements[-1].is_interruption():
                        if self.statements:
                            self.statements[-1] += ' ' + text
                            return None
                        else:
                            stype = OTHER
                else:
                    if text[0] in LOWERCASE_LETTERS:
                        if self.statements[-1]:
                            self.statements[-1] += text
                            return None

                stype = OTHER
        '''
        if self.statements:
            if stype == OTHER and not speaker and not party and self.statements[-1]:
                if self.statements[-1].is_interruption():
                    if not self.statements[-2].is_interruption():
                        prev_s = self.statements[-2]
                    elif not self.statements[-3].is_interruption():
                        prev_s = self.statements[-3]
                    else:
                        prev_s = self.statements[-4]
                    stype = prev_s.type
                    speaker = prev_s.speaker
                    party = prev_s.party
        '''
        s = '[%s] %s (%s): - %s\n\n' % (stype, speaker, party, text)
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

                            else:
                                if el.name == 'br':
                                    # line break
                                    p += '\\n'
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

        self._extract_metadata()
        return self.statements

    def _extract_metadata(self):
        lines = self.statements[0].split('\\n')
        pprint(lines)

        for line in lines:
            line = line.strip()

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
                name = line.replace('Presidente: ', '')
                name = name.replace('Ex.mo Sr. ', '')
                self.president = name

            elif line.startswith('Secretários: '):
                logging.info('QDParser: Secretaries found!')
                line_index = lines.index(line) 

                name = line.replace('Secretários: ', '')
                name = name.replace('Ex.mos Srs. ', '')

                names = []

                while name:
                    names.append(name)
                    line_index += 1
                    name = lines[line_index]

                self.secretaries = names

            elif line.startswith(('SUMÁRIO', 'S U M Á R I O')):
                logging.info('QDParser: Summary found!')
                self.summary = ''
                line_index = lines.index(line) 
                for line in lines[line_index:]:
                    self.summary += line + '\n'
                self.summary = self.summary.replace('SUMÁRIO', '').strip()
                break
                
        if not self.president: logging.error('President not found') 
        if not self.date: logging.error('Session date not found') 
        if not self.secretaries: logging.error('Secretaries not found') 
        if not self.summary: logging.error('Summary not found') 






    def get_txt(self):
        output = ''
        for s in self.statements:
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
    outfilename = filename + ext
    outfile = open(outfilename, 'w')
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
