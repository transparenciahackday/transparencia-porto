#!/usr/bin/env python
#-*- coding: utf-8 -*-
import sys
from BeautifulSoup import BeautifulStoneSoup

def remove_double_newlines(txt):
    # recursive fun
    newtxt = txt.replace('\n\n\n', '\n\n')
    if '\n\n\n' in newtxt:
        newtxt = remove_double_newlines(newtxt)
    return newtxt

def is_single_bold_line(line):
    l = line.strip('\n., ')
    if l.startswith('*') and l.endswith('*') and not '\n' in l:
        return True
    return False
def is_single_italic_line(line):
    l = line.strip('\n.,: ')
    if l.startswith('_') and l.endswith('_'):
        return True
    return False
def reformat_italic_line(line):
    # convert italic lines to square brackets
    # fix non-italic full stops
    new_line = line.replace('_.', '._')
    new_line = new_line.replace('_:', ':_')
    new_line = new_line.replace('_', '[', 1)
    new_line = new_line.replace('_', ']', 1)
    if '_' in new_line:
        print new_line
        assert False
    return new_line

def fix_italics(line):
    #if not line.startswith('_') and line.endswith('_'):
    #    return line
    return line.replace('_ _', ' ')

def is_irrelevant(entry):
    if (not entry or
        entry.startswith(u'_Presenças e faltas dos Deputados') or
        u'A DIVISÃO DE RED' in entry or
        entry.startswith((u'*Segunda', u'*Terça', u'*Quarta', u'*Quinta', u'*Sexta', u'*Sábado')) or
        entry.startswith((u'1.ª SESSÃO', u'2.ª SESSÃO', u'3.ª SESSÃO', u'4.ª SESSÃO'))
        ):
        return True
    return False

def correct_newlines(entry):
    if not '\n' in entry:
        return entry
    new_entry = u''
    lines = entry.split('\n')
    for line in lines:
        if (not line.strip().endswith(('.', ':', '?', '!')) or
            lines.index(line) == len(lines)-1 or # last line?
            line.strip().endswith(('Sr.', 'Srs.'))
            ):
            new_entry += (line)
        else:
            new_entry += (line + '\n')
    return new_entry

def split_speaker(entry):
    parts = entry.split(u': — ')
    if len(parts) == 1:
        return entry
    elif len(parts) == 2:
        speaker, text = parts
        # TODO: Regex?
        speakername = speaker.split('*')[1]
        try:
            speakertitle = speaker.split('(')[1].rstrip(')')
            if speakername.startswith(('Ministr', u'Secretário de Estado', u'Secretária de Estado', 'Primeiro-Ministro')):
                # switch
                new_entry = '%s (%s):\n%s' % (speakertitle, speakername, text)
            else:
                new_entry = '%s (%s):\n%s' % (speakername, speakertitle, text)
        except IndexError:
            # no title or party
            new_entry = '%s:\n%s' % (speakername, text)
        return new_entry
    else:
        raise ValueError('Problem splitting speaker from text, too many parts')

def scrape_metadata(lines):
    # regexes para data (reunião plenária)
    # sessão legislativa
    # retirar número do filename
    # nome presidente, secretários
    # apagar tudo até à primeira fala da presidente
    pass

def remove_rollcalls(lines):
    # títulos das chamadas
    # nomes completos de deputados
    # nomes de partidos
    # presentes começam depois da primeira indicação de hora
    # os outros estão no final
    pass

source = open(sys.argv[1], 'r').read()
txt = remove_double_newlines(source)
entries = txt.split('\n\n')
parsed_entries = []
for entry in entries:
    entry = unicode(entry, 'utf-8')
    if is_irrelevant(entry):
        continue

    entry = correct_newlines(entry)
    entry = split_speaker(entry)

    entry = fix_italics(entry)
    if is_single_italic_line(entry):
        entry = reformat_italic_line(entry)

    parsed_entries.append(entry)

parsed_txt = u'\n\n'.join(parsed_entries)
import codecs
outfile = codecs.open(sys.argv[2], 'w', 'utf-8')
outfile.write(parsed_txt)
outfile.close()

