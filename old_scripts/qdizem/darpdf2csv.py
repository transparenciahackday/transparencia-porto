#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
darpdf2csv
Copyright 2010 ricardo lafuente <ricardo@hacklaviva.net>
Distribuído nos termos da GNU General Public License v3 ou posterior.

Um script para converter um conjunto de ficheiros do DAR para formato CSV.
Mais info: http://transparencia.hacklaviva.net

É usado em conjunto com o qdizem.py para navegar uma estrutura de directórios e
criar uma estrutura idêntica com versões CSV dos documentos.

Antes de o correr, há que modificar as variáveis SOURCEDIR e DESTDIR para
corresponder aos directórios que temos.

Dúvidas? E-mail ricardo at hacklaviva.net !
'''


import os

SOURCEDIR = '../../dar-pdf'
DESTDIR = '../../datasets/transcricoes/dar-1'
SCRIPT = './qdizem.py'

if not os.path.exists(DESTDIR):
    os.mkdir(DESTDIR)

tree = os.walk(SOURCEDIR)
for root, dirs, files in tree:
    if dirs:
        for dir in dirs:
            # FIXME: isto está aqui enquanto testo, é preciso tirar
            # quando for pra parsar tudo
            if dir != '11leg-1':
                continue
            # criar o dir na pasta destino caso não exista
            if not os.path.exists(os.path.join(DESTDIR, dir)):
                os.mkdir(os.path.join(DESTDIR, dir))
            path = os.path.join(root, dir)
            for file in os.listdir(path):
                # ignora ficheiros que não sejam PDFs, ou sumários
                if not os.path.splitext(file)[-1] == '.pdf' or not file.startswith('DAR'):
                    continue
                # determina o nome do ficheiro csv
                # target = os.path.join(DESTDIR, dir, file)
                # meter extensão csv
                # target = os.path.splitext(target)[0] + '.csv'
                # apagar ficheiro antigo
                # if os.path.exists(target):
                #    os.remove(target)
                # usa agora uma linha bash para criar o csv com o script de conversão
                command = 'python %s %s' % (SCRIPT, os.path.join(path, file))
                # print command
                os.system(command)

