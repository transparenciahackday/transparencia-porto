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
        elif e.text.endswith((u' seguinte:', u'seguintes:')) or e.text.startswith('Ata') or e.text.startswith('Propostas apresentadas'):
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
        e.party = u'Presidente da República'
        e.type = PR_STATEMENT

    elif e.party in PARTIES:
        e.type = MP_STATEMENT
    elif e.speaker.startswith(('Vozes', 'Uma voz d')):
        e.type = VOICES_ASIDE

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
    entries_to_remove = []
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
        elif lines[0].endswith(':') and len(lines[0]) < 100 and not lines[0].startswith(('Relativa', 'A acta', 'O artigo', 'Agora,', 'Por fim,', 'Segue-se',)):
            e.speaker, e.party, e.type = get_speaker(lines[0])
            e.text = '\n'.join(lines[1:])

        # não encontra tipo? ver se é quebra de linha errada, ou continuação, ou documento
        # TODO: Fazer uma função para poder ver recursivamente no caso de várias null seguidas
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
            elif prev_e.type in INTERRUPTIONS and prev_e.get_previous().type in (STATEMENT, CONT):
                e.speaker = prev_e.get_previous().speaker
                e.party = prev_e.get_previous().party
                e.type = CONT
            # duas interrupções seguidas
            elif prev_e.type in INTERRUPTIONS and prev_e.get_previous().type in INTERRUPTIONS and prev_e.get_previous(steps=2).type in (STATEMENT, CONT):
                e.type = CONT
            else:
                print 'Continuação não identificada:'
                print '  - ' + str(prev_e.get_previous().get_previous().type)
                print '  - ' + str(prev_e.get_previous().type)
                print '  - ' + str(prev_e.type)
                print '  - ' + str(e.type)
                print e.text.encode('utf-8')
                print

    # mais uma passagem para remover restos da verificação dos órfãos
    entries_to_remove.reverse()
    for e in entries_to_remove:
        s.entries.pop(e)

    # third pass: tipos especificos de intervencao
    entries_to_remove = []
    for e in s.entries:
        if not e.type == STATEMENT:
            continue
        parse_statement(e)
        if e.type == PRESIDENT_STATEMENT:
            parse_president_statement(e)
        # colar continuações da mesma intervenção
        # FIXME este passo é destrutivo e pode ser perigoso, precisamos de unit tests aqui
        elif e.type == CONT: 
            prev_e = e.get_previous()
            if not e.speaker and not e.party and prev_e().type == MP_STATEMENT:
                # parágrafo solto!
                if prev_e().text.strip().endswith(('.','?','!', ':')):
                    prev_e().text += '\n' + e.text
                else:
                    prev_e().text += ' ' + e.text
                entries_to_remove.append(s.entries.index(e))
                e.type = MP_STATEMENT
            # elif e.type in PRESIDENT_STATEMENTS
            # TODO: elif prev_e.type in INTERRUPTIONS:


    entries_to_remove.reverse()
    for e in entries_to_remove:
        s.entries.pop(e)
    # fourth pass: mp_id, identidades de ministros, secs. estado, pm

    
    # verificar que entradas unicas nao estao repetidas (data, nomes pres e secretarios)
    # apagar separadores, sumário

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
    
    import codecs
    outfile = codecs.open(sys.argv[2], 'w', 'utf-8')
    outfile.write(s.get_json())
    outfile.close()
