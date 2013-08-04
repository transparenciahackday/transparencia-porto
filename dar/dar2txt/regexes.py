#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

# Importa notar que algumas destas regexes são unicode, por causa dos hífens (o Python não os vai
# encontrar de outra forma)

re_hora = (re.compile(ur'^Eram (?P<hours>[0-9]{1,2}) horas e (?P<minutes>[0-9]{1,2}) minutos.$', re.UNICODE), '')

# Separador entre orador e intervenção (algumas gralhas e inconsistências obrigam-nos
# a ser relativamente permissivos ao definir a expressão)
re_separador = (re.compile(ur'\:?[ \.]?[\–\–\—\-] ', re.LOCALE|re.UNICODE), ': -')
re_separador_estrito = (re.compile(ur'\: [\–\–\—\-] ', re.LOCALE|re.UNICODE), ': - ')
re_mauseparador = (re.compile(ur'(?P<prevchar>[\)a-z])\:[ \.][\–\–\—\-](?P<firstword>[\w\»])', re.LOCALE|re.UNICODE), '\g<prevchar>: - \g<firstword>')

re_titulo = (re.compile(ur'(O Sr[\.:])|(A Sr\.?(ª)?)'), '')

re_ministro = (re.compile(ur'^Ministr'), '')
re_secestado = (re.compile(ur'^Secretári[oa] de Estado.*:'), '')

re_palavra = (re.compile(ur'(dou|tem|vou dar)(,?[\w ^,]+,?)? a palavra|faça favor[^ de terminar]', re.UNICODE|re.IGNORECASE), '')

re_concluir = (re.compile(ur'(tempo esgotou-se)|(([Pp]eço-lhe o favor de|faça (o )?favor de|eço-lhe para|tem que) (concluir|continuar|terminar))|(esgotou-se o( seu)? tempo)|((tem (mesmo )?de|queira) (terminar|concluir))|((ultrapassou|esgotou|terminou)[\w ,]* o (seu )?tempo)|((peço|solicito)(-lhe)? que (termine|conclua))|(atenção ao tempo)|(remate o seu pensamento)|(atenção para o tempo de que dispõe)|(peço desculpa mas quero inform)|(deixem ouvir o orador)|(faça favor de prosseguir a sua)|(poder prosseguir a sua intervenção)|(está a ser descontado durante)', re.UNICODE|re.IGNORECASE), '')

re_president = (re.compile(ur'O Sr\.?|A Sr\.?ª? Presidente\ ?(?P<nome>\([\w ]+\))?(?P<sep>\:[ \.]?[\–\–\—\-])'), '')

re_cont = (re.compile(ur'O Orador|A Oradora(?P<sep>\:[ \.]?[\–\–\—\-\-])', re.UNICODE), '')

re_voto = (re.compile(ur'^Submetid[oa]s? à votação', re.UNICODE), '')

re_interv = (re.compile(ur'^(?P<titulo>O Sr[\.:]?|A Sr[\.:]?(ª)?)\ (?P<nome>[\w ,’-]+)\ ?(?P<partido>\([\w -]+\))?(?P<sep>\:?[ \.]?[\–\–\—\-]? ?)', re.UNICODE), '')
re_interv_semquebra = (re.compile(ur'(?P<titulo>O Sr\.?|A Sr(\.)?(ª)?)\ (?P<nome>[\w ,’-]{1,30})\ ?(?P<partido>\([\w -]+\))?(?P<sep>\:[ \.]?[\–\–\—\-])', re.UNICODE), '')

re_interv_simples = (re.compile(ur'^(?P<nome>[\w ,’-]+)\ ?(?P<partido>\([\w -]+\))?\ ?(?P<sep>\:?[ \.]?[\–\–\—\-]? )', re.UNICODE), '')
