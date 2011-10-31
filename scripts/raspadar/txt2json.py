#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import json
import datetime
import re
import logging
logging.basicConfig(level=logging.WARNING)

SOURCE_DIR = './tagtxt/'
TARGET_DIR = './csv/'

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

REAL_STATEMENTS = (MP_STATEMENT, GOV_STATEMENT, PRESIDENT_STATEMENT, INTERRUPTION, SECRETARY_STATEMENT, MP_CONT, PM_STATEMENT, MINISTER_STATEMENT, STATE_SECRETARY_STATEMENT, STATEMENT, MP_ASIDE, PRESIDENT_ASIDE, PRESIDENT_NEWSPEAKER)

re_separador = (re.compile(ur'\:?[ \.]?[\–\–\—\-] ', re.UNICODE), ': - ')

REPLACES = [
        (re.compile(ur'dastrabalhadoras', re.UNICODE), 'das trabalhadoras'),
        (re.compile(ur'deeuros', re.UNICODE), 'de euros'),
        (re.compile(ur'sms', re.UNICODE), 'SMS'),
        (re.compile(ur'Mubarack', re.UNICODE), 'Mubarak'),
        (re.compile(ur'Bourgiba', re.UNICODE), 'Bourguiba'),
        (re.compile(ur'Merkl', re.UNICODE), 'Merkel'),
        (re.compile(ur'háde', re.UNICODE), 'há de'),
        (re.compile(ur'digolhe', re.UNICODE), 'digo-lhe'),
        (re.compile(ur'peco-lhe', re.UNICODE), 'peço-lhe'),
        (re.compile(ur'O S. Agostinho Lopes', re.UNICODE), 'O Sr. Agostinho Lopes'),
        (re.compile(ur'Deputado falou: - ', re.UNICODE), 'Deputado falou - '),
        (re.compile(ur'^Sr. Pedro Mota Soares', re.UNICODE), 'O Sr. Pedro Mota Soares'),

    ]

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

    def get_json(self):
        real_statements = []
        for s in self.statements:
            if s.type not in (INTRO, ROLLCALL_PRESENT, ROLLCALL_ABSENT, ROLLCALL_MISSION, ROLLCALL_LATE, SUMMARY, TIME):
                real_statements.append(s)
        sess = {
                'session-date': self.date,

                'president': self.president,
                'secretaries': self.secretaries,

                'time_start': self.time_start,
                'time_end': self.time_end,

                'summary': self.summary,
                'entries': [s.as_dict for s in real_statements],
                'rollcall': {
                             'present': '',
                             'absent': '',
                             'mission': '',
                             'late': '',
                            }

                }
        output = ''
        for s in self.statements:
            if s.text.strip('\n '):
                output += json.dumps(s.as_dict, encoding='utf-8', ensure_ascii=False, sort_keys=True, indent=1)
                # output += s.as_csv + '\n'
            else:
                print 'Empty statement found.'
        # return output
        return json.dumps(sess, encoding='utf-8', ensure_ascii=False, sort_keys=True, indent=1)

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
        return "%s|%s|%s|%s" % (self.type, self.speaker, self.party, self.text)
    @property
    def as_csv(self):
        return "%s|%s|%s|%s" % (self.type, self.speaker, self.party, self.text)
    @property
    def as_dict(self):
        return {'type': self.type,
                'speaker': self.speaker,
                'party': self.party,
                'text': self.text.replace('\\n', '\n')
                }

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
        for line in self.lines:
            if not line.strip():
                continue

            line = line.decode('utf-8') 
            # print type(line)

            speaker = ''
            party = ''

            stype, remainder = line.split(']', 1)
            stype = stype.strip('[')
            remainder = remainder.strip('\n ')

            if stype in REAL_STATEMENTS:
                try:
                    speakerparty, text = re.split(re_separador[0], remainder, 1)
                    speakerparty = speakerparty.strip()
                except:
                    print stype
                    print remainder
                    print re.search(re_separador[0], remainder)
                    raise

                if '(' in speakerparty:
                    speaker, party = speakerparty.split('(', 1)
                    party = party.strip(')')
                elif stype.startswith('president') or stype in (INTERRUPTION, PM_STATEMENT): 
                    speaker = speakerparty
                    party = ''
                elif speakerparty == 'Primeiro-Ministro':
                    # FIXME: Map who is the prime minister in this legislature!
                    speaker = 'Primeiro-Ministro'
                    party = ''
                else:
                    print '  Type:         ' + stype
                    print '  Speakerparty: ' + speakerparty
                    print '  Text:         ' + text
                    assert False
            else:
                speaker = ''
                party = ''
                text = remainder

            text = text.strip('\n ')
            text = text.replace('\n', '\\n')
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

    def prune_statements(self):
        pass
        # remover as primeiras linhas (título, lista de presenças,
        # sumário) até ao Presidente falar

        # TODO: retirar chamada, intro

        # chegando à encerrada (existe?), acabou o que interessa

    def run(self):
        del self.session
        self.session = Session()
        #self._get_metadata()
        self._get_statements()

    def flush(self):
        self.session.flush_statements()
        self.session = Session()

def parse_tagtxt_file_to_json(infile, outfile):
    lines = open(infile, 'r').read().split('\n\n')
    parser = QDTextParser(lines)
    try:
        parser.run()
    except:
        logging.error('Tagging error in file %s.' % (infile))
        raise

    import codecs
    outfile = codecs.open(outfile, 'w', 'utf-8-sig')
    outfile.write(parser.session.get_json())
    outfile.close()

if __name__ == '__main__':
    from ConfigParser import SafeConfigParser

    # analisar o ficheiro config
    parser = SafeConfigParser()
    parser.read('raspadar.conf')
    default_input = os.path.abspath(parser.get('taggedtext2csv', 'sourcedir'))
    default_output = os.path.abspath(parser.get('taggedtext2csv', 'targetdir'))

    # analisar as opções da linha de comandos
    import optparse
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
                output = input.replace('.tag.txt', '.json')
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
        for f in glob.glob(os.path.join(input, '*.tag.txt')):
            if output:
                inputs[f] = os.path.join(output, os.path.basename(f).replace('.tag.txt', '.json'))
            else:
                # sem output -> grava o txt no mesmo dir
                inputs[f] = os.path.join(input, os.path.basename(f).replace('.tag.txt', '.json'))
        for i in inputs:
            if os.path.exists(inputs[i]) and not options.force:
                print 'File %s exists, not overwriting.' % inputs[i]
                continue
            if verbose: print '  %s -> %s' % (i, inputs[i])
            try:
                parse_tagtxt_file_to_json(i, inputs[i])
                successes.append(i)
            except:
                outfile = open(inputs[i], 'w')
                outfile.close()
                if picky:
                    sys.exit()
                failures.append(i)
        if verbose:
            print '----------------------------------'
            print 'Successfully parsed:   %d files' % (len(successes))
            print 'Failed:                %d files' % (len(failures))
            print '----------------------------------'
                
    else:
        parse_tagtxt_file_to_json(input, output)
