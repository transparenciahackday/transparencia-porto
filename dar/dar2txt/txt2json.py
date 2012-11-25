#!/usr/bin/env python
#-*- coding: utf-8 -*-
import sys
import json
import re
from entrytypes import *

UNKNOWN_NOTE = 'note_unknown'
SPEAKER_ERROR = 'speaker_error'

MONTHS = {'janeiro': 1, 'fevereiro': 2, u'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
          'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12}
PARTIES = ('PSD', 'PS', 'CDS-PP', 'PCP', 'BE', 'Os Verdes', 'PEV')


class Session:
    def __init__(self):
        self.date = None
        self.entries = []
        self.time_start = None
        self.time_end = None
        
        self.president = ''
        self.secretaries = []
        self.summary = ''

    def get_json(self):
        sess = {
                'session-date': self.date,
                'president': self.president,
                'secretaries': self.secretaries,
                'time_start': self.time_start,
                'time_end': self.time_end,

                'entries': [e.as_dict for e in self.entries],
                }
        return json.dumps(sess, encoding='utf-8', ensure_ascii=False, sort_keys=True, indent=1)
    
class Entry:
    def __init__(self, session=None):
        self.speaker = None
        self.party = None
        self.type = None
        self.mp_id = None

        self.session = session

    def get_previous(self, steps=1):
        entries = self.session.entries
        return entries[entries.index(self) - steps]

    def __str__(self):
        return "<Entry %s; %s (%s): %s>" % (self.type, self.speaker, self.party, self.text[:30])
    @property
    def as_csv(self):
        return "%s|%s|%s|%s" % (self.type, self.speaker, self.party, self.text)
    @property
    def as_dict(self):
        entrydict = {'type': self.type, 'text': self.text}
        if self.speaker: entrydict['speaker'] = self.speaker
        if self.party: entrydict['party'] = self.party
        return entrydict


def get_note_type(e):
    # para esta função ser chamada, já sabemos que o texto da entrada começa com '['
    # primeiro, remover itálicos lá dentro
    e.text = e.text.replace('_', '')
    if e.text.endswith(']'):
        # oneliner
        e.text = e.text.strip('[]')
        if e.text.startswith(u'Protesto'):
            return PROTEST
        elif e.text.startswith(u'Risos'):
            return LAUGHTER
        elif e.text.startswith(u'Aplauso'):
            return APPLAUSE
        elif e.text.startswith(u'Pausa'):
            return PAUSE
        elif e.text.startswith(u'Eram ') and e.text.endswith(('horas.', 'minutos.', 'minuto.')):
            return TIME
        elif e.text.startswith(u'Nota'):
            return NOTE
        elif e.text.startswith(u'Submetid') or e.text == u'Procedeu-se à votação.':
            return VOTE
        elif e.text.startswith((u'——', u'——')):
            return SEPARATOR
        elif e.text.startswith(u'Sumário'):
            return SUMMARY
        elif e.text.endswith(u'de silêncio.'):
            return SILENCE
        elif u'assumiu a presidência' in e.text or u'assumiu a Presidência' in e.text:
            return PRESIDENT_SWITCH
        elif e.text.startswith(u'Nota') or e.text.startswith(u'Neste momento,'):
            return NOTE
        elif ('ocuparam os seus lugares' in e.text or 
              'tomou a palavra' in e.text  or 
              'ocupou o seu lugar' in e.text or
              'Imagens' in e.text or
              e.text.startswith('Registaram-se protestos')):
            return NOTE
        elif e.text.endswith(('2009', '2010', '2011', '2012')):
            parse_session_date(e)
            return DATE
        elif e.text.endswith((u' seguinte:', u'seguintes:', u'seguinte teor:')) or e.text.startswith('Ata') or e.text.startswith('Propostas apresentadas'):
            return DOCUMENT_START
        elif e.text.startswith(u'Declaraç'):
            return VOTE_STATEMENT_START
        elif 'Hino Nacional' in e.text:
            return ANTHEM
        elif e.text == u'…':
            return DOCUMENT
        else:
            return UNKNOWN_NOTE
    else:
        e.text = e.text.strip('[]')
        # estes ocupam várias linhas, por isso não corresponde ao if acima
        if e.text.startswith(u'Secretários:'):
            return SECRETARY_NAME
        elif e.text.startswith(u'Presidente:'):
            return PRESIDENT_NAME
        else:
            return UNKNOWN_NOTE

def get_speaker(speakerline):
    speakerline = lines[0].strip(':')
    parts = speakerline.split('(')

    speaker = None
    party = None
    if len(parts) == 1:
        speaker = speakerline.strip()
        etype = STATEMENT
    elif len(parts) == 2:
        speaker, party = parts
        speaker = speaker.strip()
        party = party.strip(')')
        etype = STATEMENT
    else:
        etype = SPEAKER_ERROR
    return (speaker, party, etype)

def parse_statement(e):
    if e.speaker == 'Presidente':
        e.type = PRESIDENT_STATEMENT
    elif e.speaker in (u'Secretário', u'Secretária'):
        e.type = SECRETARY_STATEMENT
    elif e.party == 'Primeiro-Ministro' or e.speaker == 'Primeiro-Ministro':
        e.type = PM_STATEMENT
    elif (e.party and e.party.startswith('Ministr')) or e.speaker.startswith('Ministr'):
        e.type = MINISTER_STATEMENT
    # já detectámos antes se é o Secretário da AR, por isso agora é secretários de estado
    elif (e.party and e.party.startswith(u'Secretári')) or e.speaker.startswith(u'Secretári'):
        e.type = STATE_SECRETARY_STATEMENT
    elif e.speaker == u'Presidente da República' or e.party == u'Presidente da República':
        e.type = PR_STATEMENT
    elif e.speaker.startswith(('Vozes', 'Uma voz d')):
        e.type = VOICES_ASIDE
    elif e.party in PARTIES:
        e.type = MP_STATEMENT
    elif e.speaker.endswith(('seguinte', 'seguintes', 'seguinte teor')) or e.speaker.startswith('Ata') or e.text.startswith('Propostas apresentadas'):
        e.type = DOCUMENT_START
    else:
        # primeira linha nao identificada, marcamos como continuação para na passagem seguinte
        # ele tentar identificar
        e.type = CONT

people = {}
def parse_non_mp_statement(e):
    # membros de governo e outros
        if e.type in PM_STATEMENTS + (PM_ASIDE,):
            if e.party:
                if e.party.startswith('Primeiro'):
                    # nome mencionado, vamos adicionar à lista de pessoas
                    people[e.party] = e.speaker 
                else:
                    print 'ei!'
                    print e.speaker
                    print e.party
            elif e.speaker.startswith('Primeiro'):
                # apenas mencionado o cargo, vamos adicionar o nome
                e.party = e.speaker
                e.speaker = people[e.speaker]
            else:
                print 'Intervenção de primeiro-ministro não identificada!'
        elif e.type in MINISTER_STATEMENTS + (MINISTER_ASIDE,):
            if e.party and e.party.startswith('Ministr'):
                # nome mencionado, vamos adicionar à lista de pessoas
                people[e.party] = e.speaker 
            elif e.speaker.startswith('Ministr'):
                # apenas mencionado o cargo, vamos adicionar o nome
                e.party = e.speaker
                e.speaker = people[e.speaker]
            else:
                print 'Intervenção de ministro não identificada!'
        elif e.type in STATE_SECRETARY_STATEMENTS + (STATE_SECRETARY_ASIDE,):
            if e.party:
                if e.party.startswith(u'Secretári'):
                    # nome mencionado, vamos adicionar à lista de pessoas
                    people[e.party] = e.speaker 
                elif e.speaker.startswith(u'Secretári'):
                    if e.party:
                        # às vezes nome e cargo estão trocados...
                        people[e.speaker] = e.party
                else:
                    print 'Intervenção de sec. estado não identificada!'
                    print '- %s (%s)' % (e.speaker, str(e.party))
            else:
                # apenas mencionado o cargo, vamos adicionar o nome
                e.speaker = people[e.speaker]
                e.party = e.speaker
        elif e.type in PR_STATEMENTS + (PR_ASIDE,):
            if e.party:
                if e.party.startswith(u'Presidente'):
                    # nome mencionado, vamos adicionar à lista de pessoas
                    people[e.party] = e.speaker 
                elif e.speaker.startswith(u'Presidente'):
                    if e.party:
                        # às vezes nome e cargo estão trocados...
                        people[e.speaker] = e.party
                    else:
                        print 'Intervenção de PR não identificada!'
                        print '- %s (%s)' % (e.speaker, str(e.party))
            else:
                # apenas mencionado o cargo, vamos adicionar o nome
                e.party = e.speaker
                e.speaker = people[e.speaker]

def parse_session_date(entry):
    parts = entry.text.strip().split(' ')
    day = int(parts[0])
    month = MONTHS[parts[2]]
    year = int(parts[4])
    e.session.date = '%02d-%02d-%d' % (day, month, year)

def parse_president_statement(e):
    from regexes import re_palavra, re_concluir
    p = e.text
    if u'encerrada a sessão' in p or u'encerrada a reunião' in p:
        e.type = PRESIDENT_CLOSE
    elif (u'quórum' in p or 'quorum' in p) and 'aberta' in p:
        e.type = PRESIDENT_OPEN
    elif re.search(re_palavra[0], p):
        e.type = PRESIDENT_NEWSPEAKER
    elif re.search(re_concluir[0], p):
        e.type = PRESIDENT_ASIDE

if __name__ == "__main__":
    source = open(sys.argv[1], 'r').read()
    txt_entries = source.split('\n\n')

    # primeira passagem: converter texto em objectos Entry
    s = Session()
    for txt_entry in txt_entries:
        e = Entry(session=s)
        e.text = unicode(txt_entry.strip(), 'utf-8')
        s.entries.append(e)

    # segunda passagem: determinar tipos de cada entrada e detectar continuações
    for e in s.entries:
        entry_index = s.entries.index(e)
        lines = e.text.split('\n')
        # é uma nota de redacção? Verificar se está entre parêntesis rectos.
        if e.text.startswith('['):
            e.type = get_note_type(e)
            continue
        # é um orador? Limitamos o tamanho da linha para evitar falsos 
        # positivos onde vai ser lido um documento e que por isso acabam com ':'
        # e também checamos certas expressões que dão positivo erradamente nalguns casos
        elif lines[0].endswith(':') and len(lines[0]) < 150 and not lines[0].startswith(('Relativa', 'A acta', 'A ata', 'Acta', 'Ata', 'O artigo', 'Agora,', 'Por fim,', 'Segue-se',)) and not lines[0].endswith(('seguinte', 'seguinte teor', 'ropostas apresentadas')):
            e.speaker, e.party, e.type = get_speaker(lines[0])
            e.text = '\n'.join(lines[1:])

        # não encontra tipo? ver se é quebra de linha errada, ou continuação, ou documento
        if not e.type:
            prev_e = e.get_previous()
            
            # separador?
            if e.text.startswith(u'——') and len(e.text) < 10:
                e.type = SEPARATOR
            # conteúdos de um documento?
            elif prev_e.type == DOCUMENT_START:
                e.type = DOCUMENT
            elif prev_e.type == DOCUMENT:
                e.type = DOCUMENT
            # conteúdos de uma declaração de voto?
            elif prev_e.type == VOTE_STATEMENT_START:
                e.type = VOTE_STATEMENT
            elif prev_e.type == VOTE_STATEMENT:
                e.type = VOTE_STATEMENT
            elif prev_e.type == SEPARATOR and (prev_e.get_previous().type == VOTE_STATEMENT or e.text.startswith('Relativ')):
                e.type = VOTE_STATEMENT
            # sumário? 
            elif prev_e.type == SUMMARY:
                e.type = SUMMARY
            # continuação?
            elif prev_e.type in (STATEMENT, CONT):
                # continuação da intervenção/continuação anterior! Vamos juntá-las mais à frente,
                # para já marcamos como continuação
                e.type = CONT
            elif prev_e.type in INTERRUPTIONS+ASIDES:
                # interrupções seguidas?
                while prev_e.type in INTERRUPTIONS+ASIDES:
                    prev_e = prev_e.get_previous()
                if prev_e.type in (STATEMENT, CONT):
                    e.speaker = prev_e.speaker
                    e.party = prev_e.party
                    e.type = CONT
                else:
                    print 'Continuação não identificada:'
                    print '  - ' + str(e.get_previous(3).type)
                    print '  - ' + str(e.get_previous(2).type)
                    print '  - ' + str(e.get_previous().type)
                    print '  - ' + str(e.type)
                    print e.text.encode('utf-8')
                    print
            elif prev_e.type in INTERRUPTIONS and prev_e.get_previous().type in INTERRUPTIONS and prev_e.get_previous(steps=2).type in (STATEMENT, CONT):
                e.type = CONT
            else:
                print 'Continuação não identificada:'
                print '  - ' + str(e.get_previous(3).type)
                print '  - ' + str(e.get_previous(2).type)
                print '  - ' + str(e.get_previous().type)
                print '  - ' + str(e.type)
                print e.text.encode('utf-8')
                print

    # third pass: tipos especificos de intervencao e remover entradas que nao precisamos
    entries_to_remove = []
    for e in s.entries:
        if e.type in (DATE, SUMMARY, PRESIDENT_NAME, SECRETARY_NAME):
            entries_to_remove.append(s.entries.index(e))
        # intervenção
        elif e.type == STATEMENT:
            parse_statement(e)
            if e.type == PRESIDENT_STATEMENT:
                parse_president_statement(e)
    # colar continuações da mesma intervenção
    # FIXME este passo é destrutivo e pode ser perigoso, precisamos de unit tests aqui
    for e in s.entries:
        if e.type == CONT: 
            prev_e = e.get_previous()
            if not e.speaker and not e.party:
                if prev_e.type in STATEMENTS:
                    # parágrafo solto!
                    # assegurar que não é uma das que marcámos para apagar
                    while prev_e.type in INTERRUPTIONS+ASIDES or prev_e in entries_to_remove:
                        prev_e = prev_e.get_previous()
                    # distinguir entre quebras de linha e de parágrafo
                    if prev_e.text.strip().endswith(('.','?','!', ':')):
                        prev_e.text += '\n' + e.text
                    else:
                        prev_e.text += ' ' + e.text
                    entries_to_remove.append(s.entries.index(e))
                    e.type = STATEMENT
    entries_to_remove.reverse()
    for e in entries_to_remove:
        s.entries.pop(e)

    # nova passagem: catalogar continuações
    # fazemos duas passagens aqui
    for n in range(2):
        for e in s.entries:
            if e.type == CONT:
                if not e.party and not e.speaker:
                    prev_e = e.get_previous()
                    if prev_e.type in INTERRUPTIONS+ASIDES:
                        # interrupções seguidas?
                        while prev_e.type in INTERRUPTIONS+ASIDES:
                            prev_e = prev_e.get_previous()

                    if prev_e.type in MP_STATEMENTS:
                        e.type = MP_CONT
                        e.speaker = prev_e.speaker
                        e.party = prev_e.party
                    elif prev_e.type in PRESIDENT_STATEMENTS:
                        e.type = PRESIDENT_CONT
                        e.speaker = prev_e.speaker
                        e.party = prev_e.party
                    elif prev_e.type in PM_STATEMENTS:
                        e.type = PM_CONT
                        e.speaker = prev_e.speaker
                        e.party = prev_e.party
                    elif prev_e.type in MINISTER_STATEMENTS:
                        e.type = MINISTER_CONT
                        e.speaker = prev_e.speaker
                        e.party = prev_e.party
                    elif prev_e.type in STATE_SECRETARY_STATEMENTS:
                        e.type = STATE_SECRETARY_CONT
                        e.speaker = prev_e.speaker
                        e.party = prev_e.party
                    elif prev_e.type in PR_STATEMENTS:
                        e.type = PR_CONT
                        e.speaker = prev_e.speaker
                        e.party = prev_e.party
                    elif prev_e.type in SECRETARY_STATEMENTS:
                        e.type = SECRETARY_CONT
                        e.speaker = prev_e.speaker
                        e.party = prev_e.party
                    elif prev_e.type == DOCUMENT_START:
                        e.type = DOCUMENT
                    elif prev_e.type == DOCUMENT:
                        e.type = DOCUMENT
                    # conteúdos de uma declaração de voto?
                    elif prev_e.type == VOTE_STATEMENT_START:
                        e.type = VOTE_STATEMENT
                    elif prev_e.type == VOTE_STATEMENT:
                        e.type = VOTE_STATEMENT
                    elif prev_e.type == SEPARATOR and (prev_e.get_previous().type == VOTE_STATEMENT or e.text.startswith('Relativ')):
                        e.type = VOTE_STATEMENT
                    else:
                        print prev_e.type
                else:
                    prev_e = e.get_previous()
                    if prev_e.type in INTERRUPTIONS+ASIDES:
                        # interrupções seguidas?
                        while prev_e.type in INTERRUPTIONS+ASIDES:
                            prev_e = prev_e.get_previous()
                    if prev_e.type in MP_STATEMENTS:
                        e.type = MP_CONT
                    elif prev_e.type in PRESIDENT_STATEMENTS:
                        e.type = PRESIDENT_CONT
                    elif prev_e.type in PM_STATEMENTS:
                        e.type = PM_CONT
                    elif prev_e.type in MINISTER_STATEMENTS:
                        e.type = MINISTER_CONT
                    elif prev_e.type in STATE_SECRETARY_STATEMENTS:
                        e.type = STATE_SECRETARY_CONT
                    elif prev_e.type in PR_STATEMENTS:
                        e.type = PR_CONT
                    elif prev_e.type in SECRETARY_STATEMENTS:
                        e.type = SECRETARY_CONT
                    elif prev_e.type == DOCUMENT_START:
                        e.type = DOCUMENT
                    elif prev_e.type == DOCUMENT:
                        e.type = DOCUMENT
                    # conteúdos de uma declaração de voto?
                    elif prev_e.type == VOTE_STATEMENT_START:
                        e.type = VOTE_STATEMENT
                    elif prev_e.type == VOTE_STATEMENT:
                        e.type = VOTE_STATEMENT
                    elif prev_e.type == SEPARATOR and (prev_e.get_previous().type == VOTE_STATEMENT or e.text.startswith('Relativ')):
                        e.type = VOTE_STATEMENT
                    else:
                        print prev_e.type

    # encontrar apartes
    for e in s.entries:
        if e.type in STATEMENTS:
            prev_e = e.get_previous()
            # FIXME: preguiça -- consideramos intervenções curtas como apartes
            while prev_e.type in INTERRUPTIONS+ASIDES:
                prev_e = prev_e.get_previous()
            if (e.type == MP_STATEMENT and prev_e.type in MP_STATEMENTS and 
                e.speaker and not e.speaker == prev_e.speaker and
                len(e.text) < 100):
                e.type = MP_ASIDE
            
            elif prev_e.type in MP_STATEMENTS and prev_e.speaker == e.speaker:
                e.type = MP_CONT
            elif prev_e.type in PRESIDENT_STATEMENTS and prev_e.speaker == e.speaker:
                e.type = PRESIDENT_CONT
            elif prev_e.type in MINISTER_STATEMENTS and prev_e.speaker == e.speaker:
                e.type = MINISTER_CONT
            elif prev_e.type in PM_STATEMENTS and prev_e.speaker == e.speaker:
                e.type = PM_CONT
            elif prev_e.type in STATE_SECRETARY_STATEMENTS and prev_e.speaker == e.speaker:
                e.type = STATE_SECRETARY_CONT
            elif prev_e.type in PR_STATEMENTS and prev_e.speaker == e.speaker:
                e.type = PR_CONT

    # identificar ministros e outros membros do governo
    for e in s.entries:
        if e.type in (MINISTER_STATEMENTS + PM_STATEMENTS + STATE_SECRETARY_STATEMENTS + PR_STATEMENTS + 
                     (MINISTER_ASIDE, PM_ASIDE, STATE_SECRETARY_ASIDE, PR_ASIDE)):
            parse_non_mp_statement(e)

    # concatenar declarações de voto e documentos
    entries_to_remove = []
    for e in s.entries:
        if e.type == VOTE_STATEMENT:
            prev_e = e.get_previous()
            while prev_e.type == VOTE_STATEMENT or prev_e in entries_to_remove:
                prev_e = prev_e.get_previous()
            prev_e.text += '\n' + e.text
            entries_to_remove.append(s.entries.index(e))
    entries_to_remove.reverse()
    for e in entries_to_remove:
        s.entries.pop(e)

    # final pass: look for unidentified tags
    # raw_input para confirmar se é continuação?
    for e in s.entries:
        if e.type in (UNKNOWN_NOTE, SPEAKER_ERROR):
            print 'Error %s:' % e.type
            if e.type == SPEAKER_ERROR:
                print e.speaker
                print e.party
            print e.text.encode('utf-8')
            print
        if e.type == STATEMENT:
            print 'Unparsed statement!'
            print '  ' + e.speaker.encode('utf-8')
            if e.party: print '  ' + e.party.encode('utf-8')
            print '  ' + e.text.encode('utf-8')
            print
        if e.type == UNKNOWN_NOTE:
            e.type = NOTE
        if e.type == CONT:
            print 'Continuação não identificada (última passagem):'
            print '  - ' + str(e.get_previous(3).type)
            print '  - ' + str(e.get_previous(2).type)
            print '  - ' + str(e.get_previous().type)
            print '  - ' + str(e.type)
            print e.text.encode('utf-8')
            print
        if not e.type:
            print "Entrada sem tipo!"
            print e.speaker
            print e.party
            print e.text
            print e.type

    import codecs
    outfile = codecs.open(sys.argv[2], 'w', 'utf-8')
    outfile.write(s.get_json())
    outfile.close()
