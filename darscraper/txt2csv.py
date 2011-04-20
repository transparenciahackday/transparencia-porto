
SOURCE_DIR = './txt-1/'
TARGET_DIR = './csv/'

MP_STATEMENT = 'mp'
PRESIDENT_STATEMENT = 'president'
STATEMENT = 'statement'
INTERRUPTION = 'interruption'
APPLAUSE = 'applause'
PROTEST = 'protest'
LAUGHTER = 'laughter'
NOTE = 'note'
OTHER = 'other'

class Session:
    def __init__(self, date, statements):
        self.date = date
        self.statements = statements
        self.time_start = None
        self.time_end = None
        self.summary = None
        self.interruptions = []
        self.rollcall = RollCall()

    def get_statements_csv(self):
        output = ''
        for s in self.statements:
            if s:
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
        
class QDPostProcessor:
    def __init__(self, parser):
        self.session = None
        self.parser = parser
        # copy the statement list
        self.statements = list(parser.statements)
        # TODO: interrupções? 
        # formato ((timestop, timestart), (timestop, timestart))
        self.interruptions = ()
        self.date = None

    def get_date(self):
        if not self.statements:
            raise ValueError('File not parsed yet, cannot retrieve date.')
        i = 0
        for s in self.statements:
            if i<10: print s
            i += 1
            if type(s) == type([]):
                logging.error('List found inside statement list')
                continue
            looking_for = ('REUNIÃO PLENÁRIA DE', 'REUNIAO PLENÁRIA DE', 'PLENÁRIA DE')
            if s.text.strip().startswith(looking_for):
                logging.info('QDPostProcessor: Session date found!')
                try:
                    # vamos apanhar a data
                    t = s.text.strip()
                    verbose_date = s.text.split(' ')[3:]
                    day = int(verbose_date[0])
                    month = MESES[verbose_date[2]]
                    year = int(verbose_date[4].strip())
                    self.date = datetime.date(year, month, day)
                    return self.date
                except ValueError:
                    print s 
                    raise
            else:
                pass
        if not self.date:
            logging.error('QDPostProcessor.get_date: Session date not found!')

    def get_summary(self):
        summary = ''
        return summary

    def get_times(self):
        time_start = None
        time_end = None
        return time_start, time_end

    def get_rollcall(self):
        rc = RollCall()
        return rc

    def retag_statements(self):
        speaker = None
        for s in self.statements:
            if speaker:
                # truncar o nome do speaker caso seja enorme,
                # isto é o resultado de parsing mal feito
                if len(speaker) > 200:
                    speaker = speaker[:199]
                # Estamos a meio de uma intervenção, por isso os statements
                # antes de o presidente dar a palavra a outro são interrupções
            '''
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
            '''

        # detectar início e fim de cada intervenção
        # speaker - president ; tem a palavra
        # ver até o Presidente falar e o orador seguinte não ser o anterior

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
        d = self.get_date()
        time_start, time_end = self.get_times()
        self.retag_statements()
        self.prune_statements()
        self.session = Session(date=d, statements=self.statements)
        return self.session

