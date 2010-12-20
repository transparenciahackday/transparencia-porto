#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

  QDizem v0.1
  Copyright 2010 Ricardo Lafuente
  Distribuído segundo os termos da GNU General Public License v3 ou posterior

Este programa serve para processar os Diários da Assembleia da República e
cuspir os conteúdos em formato CSV. 

O código foi escrito a correr e é meio hackado. Funciona com um loop que vai
lendo cada linha e percebendo o que cada linha é -- se é o início ou continuação
de uma intervenção, ou protestos, ou aplausos.

O output do programa é
Orador|Partido|Conteúdo da intervenção

Havendo dúvidas, vinde chatear-me: ricardo@hacklaviva.net
'''

import sys, os
import datetime

# caractere usado para delimitar os campos no CSV
DELIMITER = '|'

EXCERPT = 1
FILE = 2

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


class NoFileError(Exception): pass
class WrongExtensionError(Exception): pass

class QDParser:
    def __init__(self):
        self.date = None
        self.mode = None
        self.intervs = []
        # usamos esta variável para ignorar todas as linhas iniciais antes do início da
        # transcrição propriamente dita
        self.started = False
    def open_from_file(self, filename):
        # caso seja um PDF, usa o conversor antes
        ext = os.path.splitext(filename)[1] 
        if not ext == '.txt':
            if ext == '.pdf':
                os.system('pdftotext %s' % filename)
                filename = os.path.splitext(filename)[0] + '.txt'
            else:
                raise WrongExtensionError('This can only read .txt or .pdf files.')
        txt = open(filename, 'r')
        self.lines = txt.readlines()
        self.mode = FILE

    def open_from_string(self, s):
        self.lines = s.split('\n')
        self.mode = EXCERPT

    def save_interv(self, i):
        '''Armazena a intervenção na lista de intervenções. Também aproveitamos esta
        função para fazer algum pós-processamento, caso seja preciso.'''
        speaker, party, content = i
        if speaker.startswith('Vozes'):
            # Vozes do partido
            party = party.split(' ')[-1]
        elif speaker.startswith('Ministr'):
            party = 'Ministro' 
        interv = (speaker.strip(),
                  party,
                  content.strip())
        self.intervs.append(interv)
    
    def next_line(self, line):
        # Devolve a linha seguinte à linha entregue
        index = self.lines.index(line)
        return self.lines[index + 1]

    def run(self, mode=None):
        if not mode:
            mode = self.mode

        if not self.lines:
            raise NoFileError('No file or string was loaded, run open_from_file or open_from_string first.')

        speaker = None
        content = None
        party = None

        for line in self.lines:
            # antes de mais, sacar a data, legislatura e sessão
            if line.startswith('REUNIÃO PLENÁRIA DE'):
                # vamos apanhar a data
                verbose_date = line.split(' ')[3:]
                day = int(verbose_date[0])
                month = MESES[verbose_date[2]]
                year = int(verbose_date[4].strip())
                self.date = datetime.date(year, month, day)
            if 'LEGISLATURA' in line:
                # converter numeração romana
                roman_leg = line.split(' ')[0]
                self.leg = NUMEROS_ROMANOS[roman_leg]
            if 'SESSÃO LEGISLATIVA' in line:
                sess = line.split(' ')[0]
                sess = sess.split('.')[0]
                self.sess = int(sess)
            
            if mode == FILE:
                if line.startswith('O Sr. Presidente:'):
                    self.started = True
                if not self.started:
                    continue

            # ignorar linha "Eram X horas e Y minutos"
            # FIXME: E se uma intervenção tiver 'eram'?
            if line.startswith('Eram'):
                continue

            # ignorar lista de presenças
            if "Deputados presentes à sessão" in line:
                self.started = False
                continue

            # detectar linhas vazias e cabeçalhos do PDF, ignorando-os
            if not line.strip() or line.startswith('\x0c') \
                    or line.strip().isdigit() or line.strip() == 'as':
                continue
            
            # detectar aplausos
            if line.startswith('Aplausos'):
                previous_speaker = speaker
                previous_party = party

                # armazenar a intervenção anterior
                if content:
                    interv = (speaker, party, content.strip())
                    self.save_interv(interv)

                party = line.split(' ')[-1].strip()
                party = party.rstrip('.')
                content = '*** Aplausos ***'
                speaker = ''
                interv = (speaker, party, content)
                self.save_interv(interv)

                if ': — ' in self.next_line(line):
                    # próxima linha é outra intervenção
                    speaker = previous_speaker
                    party = previous_party
                else:
                    speaker = ''
                    party = ''
                # não gravar na próxima iteração do loop
                content = ''
                continue

            # detectar protestos
            if line.startswith('Protestos'):
                previous_speaker = speaker
                previous_party = party
                # armazenar a intervenção anterior
                if content:
                    interv = (speaker, party, content.strip())
                    self.save_interv(interv)
                
                speaker = ''
                party = ' '.join(line.split(' do ')[1:]).strip()
                party = party.replace('.', '')
                if party.startswith('Deputad'):
                    # Normalmente os protestos são das bancadas, mas às vezes
                    # também são dos deputados
                    snippet = ' '.join(party.split(' ')[1:])
                    party = snippet.split(' ')[0]
                    speaker = ' '.join(snippet.split(' ')[1:])
                    # try:
                    #     speaker = speaker.split(' ')[1]
                    #     speaker = ' '.join(speaker.split(' ')[2:])
                    # except IndexError:
                    #     pass
                content = '*** Protestos ***'
                interv = (speaker, party, content)
                self.save_interv(interv)
            
                speaker = previous_speaker
                party = previous_party
                content = ''
                continue
                
            # se a linha tem a expressão ": — ", é porque é o início de uma
            # intervenção.
            if line.find(': — ') != -1:
                # aqui começa uma nova intervenção, vamos armazenar a que
                # terminou agora
                if content:
                    interv = (speaker, party, content)
                    self.save_interv(interv)        
                # início da intervenção
                speaker, content = line.split(': — ')
                speaker = speaker.replace('O Sr. ', '')
                speaker = speaker.replace('A Sr.ª ', '')
                if speaker.find('('):
                    if 'Presidente' in speaker:
                        # presidente alternativo
                        party = 'Presidente'
                        speaker = speaker.split('(')[-1].strip(')')
                    else:
                        # há indicação de partido - Deputado XPTO (PXPTO)
                        # temos de separar
                        party = speaker.split('(')[-1].strip(')')
                        speaker = speaker.split('(')[0].strip()
                    
                # atenção às newlines, só as queremos se for final de parágrafo
                # FIXME: isto é um problema no caso de 'Sr.' ou semelhantes
                if not content.strip().endswith('.'):
                    content = content.replace('\n', ' ')

            else:    
                # continuação da intervenção
                if not line.strip().endswith('.'):
                    line = line.replace('\n', ' ')
                else:
                    line = line + ' '
                # juntar ao conteúdo
                content = content + line
                content = content.rstrip('\n')
                if '\n' in content:
                    content = content.replace('\n', '\\n')

                if 'encerrada a sessão' in line:
                    # fim da sessão, não precisamos do resto.
                    break

        # armazenar a última linha
        if content:
            interv = (speaker, party, content)
            self.save_interv(interv)        

        # repor a variável
        self.started = False

    def get_csv_output(self):
        s = ''
        for speaker, party, content in self.intervs:
            s = s + '%s%s%s%s%s' % (str(speaker), DELIMITER, str(party), DELIMITER, str(content))
            s = s + ('\n')
        return s


if __name__ == '__main__':
    qdp = QDParser()
    qdp.open_from_file(sys.argv[1])
    qdp.run()

    new_filename = 'dar_1_%02d_%02d_%s.csv' % (qdp.leg, qdp.sess, str(qdp.date))
    if os.path.exists(new_filename):
        print 'Output file already exists (%s). Overwriting.' % new_filename
        os.remove(new_filename)
    f = open(new_filename, 'w')
    f.write(qdp.get_csv_output())
    f.close()
    print 'CSV criado -> %s!' % new_filename
    '''
    print 'Série:               1ª'
    print 'Legislatura:         %s' % str(qdp.leg)
    print 'Sessão parlamentar:  %s' % str(qdp.sess)
    print 'Data:                %s' % str(qdp.date)
    '''
