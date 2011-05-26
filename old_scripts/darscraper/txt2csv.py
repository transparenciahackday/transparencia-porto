#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import datetime
import logging
logging.basicConfig(level=logging.WARNING)

SOURCE_DIR = './txt/'
TARGET_DIR = './csv/'

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

REAL_STATEMENTS = (MP_STATEMENT, GOV_STATEMENT, PRESIDENT_STATEMENT, INTERRUPTION, SECRETARY)

class Session:
    def __init__(self, date=None):
        self.date = date
        self.statements = []
        self.time_start = None
        self.time_end = None
        
        self.president = ''
        self.secretaries = []
        self.summary = ''
    
        self.interruptions = []
        self.rollcall = RollCall()

    def get_statements_csv(self):
        output = ''
        for s in self.statements:
            if s:
                print s
                #output += s.as_csv.decode('utf-8') + '\n'
                output += s.as_csv + '\n'
            else:
                print 'Empty statement found.'
        return output

    def get_metadata(self):
        output = ''
        output.append('Data: %s\n' % str(self.date))
        output.append('Sumário: %s\n' % self.summary)
        output.append('Hora de início: %s\n' % str(self.time_start))
        output.append('Hora de fim: %s\n' % str(self.time_end))
        output.append('Interrupções: %s\n' % " ".join(self.interruptions))
        output.append('Deputados presentes: %s\n' % self.rollcall.present_mps)
        output.append('Deputados ausentes: %s\n' % self.rollcall.absent_mps)
        output.append('Deputados atrasados: %s\n' % self.rollcall.late_mps)
        return output

    def flush_statements(self):
        for s in self.statements:
            del s
        self.statements = []

class Statement:
    def __init__ (self, speaker='', party='', text='', stype=''):
        self.speaker = speaker
        self.party = party
        self.text = text
        self.type = stype
    def __str__(self):
        return "%s|%s|%s|%s" % (self.speaker, self.party, self.text, self.type)
    @property
    def as_csv(self):
        return "%s|%s|%s|%s" % (self.speaker, self.party, self.text, self.type)
    def is_interruption(self):
        if self.type in (INTERRUPTION, APPLAUSE, PROTEST, LAUGHTER, NOTE):
            return True
        return False
    def is_president(self):
        return self.speaker == 'Presidente' or self.party == 'Presidente'

class RollCall:
    def __init__(self):
        self.present = []
        self.late = []
        self.absent = []
    def add_present(self, name):
        self.present.append(name)
    def add_absent(self, name):
        self.absent.append(name)
    def add_late(self, name):
        self.late.append(name)
        
class QDTextParser:
    def __init__(self, lines):
        self.session = Session()
        # self.lines deve ser uma lista de linhas extraídas de um ficheiro com
        # o readlines()
        self.lines = lines

    def _get_metadata(self):
        datestring = self.lines[0].replace('Data: ', '').strip()
        year, month, day = [int(x) for x in datestring.split('-')]
        self.session.date = datetime.date(year, month, day)
         
        self.session.president = self.lines[1].replace('Presidente: ', '') 
        self.session.secretaries = self.lines[2].replace('Secretários: ', '').split(', ') 

        # remover as linhas iniciais, já não vamos precisar
        del self.lines[:6]

    def _get_statements(self):
        #from pprint import pprint
        #pprint(lines)
        for line in self.lines:
            if line == '\n':
                del line

        for line in self.lines:
            speaker = ''
            party = ''
            # Cada linha vem no formato
            if line != '\n':
                if line.startswith('**'):
                    text = line.replace('**', '').strip()
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

                elif ': - ' in line:
                    words = line.split(' ')
                    stype = words[0].strip('[]')
                    del words[0]
                    # refazer a linha sem o tag
                    line = ' '.join(words)

                    if stype in REAL_STATEMENTS:
                        speaker, text = line.split(': - ', 1)
                        if '(' in speaker:
                            try:
                                speaker, party = speaker.split('(')
                            except ValueError:
                                print speaker
                                raise
                            party = party.strip('()')
                        else:
                            party = ''
                    else:
                        speaker = party = ''
                        text = line
                else:
                    words = line.split(' ')
                    stype = words[0].strip('[]')
                    del words[0]
                    line = ' '.join(words)
                    text = line
                    speaker = ''
                    party = ''
                text = text.strip('\n ')
                speaker = speaker.strip(' ')
                party = party.strip(' ')
                s = Statement(speaker=speaker, party=party, text=text, stype=stype)
                self.session.statements.append(s)

    def _get_times(self):
        time_start = None
        time_end = None
        return time_start, time_end

    def _get_rollcall(self):
        rc = RollCall()
        return rc

    def retag_statements(self):
        pass
    '''
        speaker = None
        for s in self.statements:
            if speaker:
                # truncar o nome do speaker caso seja enorme,
                # isto é o resultado de parsing mal feito
                if len(speaker) > 200:
                    speaker = speaker[:199]
                # Estamos a meio de uma intervenção, por isso os statements
                # antes de o presidente dar a palavra a outro são interrupções
            if s.is_president() and 'em a palavra' in s.text:
                # assinalar a anterior como fim da intervenção
                prev_s = self.statements[self.statements.index(s)-1]
                if prev_s.speaker == speaker:
                    if prev_s.type == 'end':
                        prev_s.type = 'startend'
                    else:
                        prev_s.type = 'end'
                else:
                    prev_s.type = 'end'
                
                # a próxima vai ser o início de uma intervenção
                next_s = self.statements[self.statements.index(s)+1]
                speaker = next_s.speaker
                next_s.type = 'start'
                # TODO: Verificar também se o presidente disse o nome do deputado

        # detectar início e fim de cada intervenção
        # speaker - president ; tem a palavra
        # ver até o Presidente falar e o orador seguinte não ser o anterior
    '''
    def prune_statements(self):
        # remover as primeiras linhas (título, lista de presenças,
        # sumário) até ao Presidente falar:
        found = False
        for s in self.statements:
            if (s.speaker == 'Presidente' or s.party == 'Presidente') and 'aberta' in s.text:
                # já chegámos ao que interessa
                found = True
                break
            else:
                del s
        if not found:
            logging.error('Opening statement not found.')
        # vamos remover notas que dizem as horas, e a segunda é o sinal
        # que terminou a sessão
        last_time_statement_index = None
        for s in self.statements:
            if type(s) == list:
                logging.error('prune_statements: List found inside statement list.')
                continue
            t = s.text.strip()
            # retirar notas a especificar horas
            if s.text.startswith("Eram") and s.text.endswith("minutos.") and s.type == 'note':
                last_time_statement_index = self.statements.index(s)
                del s
        # chegámos ao fim, vamos pegar na última linha que recolhemos e
        # apagar tudo o que vem a seguir
        del self.statements[last_time_statement_index:]

    def run(self):
        del self.session
        self.session = Session()
        self._get_metadata()
        self._get_statements()

    def flush(self):
        self.session.flush_statements()
        self.session = Session()


if __name__ == '__main__':
    files = sys.argv[1:]
    for f in files:
        outfilename = os.path.join(TARGET_DIR, os.path.split(f)[-1].replace('.txt', '.csv'))
        print f

        if os.path.exists(outfilename):
            logging.error('File exists already. Not overwriting.')
            continue

        file_contents = open(f, 'r')
        contents = file_contents.readlines()
        file_contents.close()
        textparser = QDTextParser(contents)
        textparser.run()
        csv_contents = textparser.session.get_statements_csv()
        import codecs
        outfile = open(outfilename, 'w')
        outfile.write(csv_contents)
        outfile.close()

