#!/usr/bin/env python
#-*- coding: utf-8 -*-
import sys
from BeautifulSoup import BeautifulStoneSoup
from replaces import REPLACES

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

def rreplace(s, old, new, occurrence):
    # http://stackoverflow.com/a/2556252
    li = s.rsplit(old, occurrence)
    return new.join(li)

def reformat_italic_line(line):
    # convert italic lines to square brackets
    # fix non-italic full stops
    new_line = line.replace('_.', '._')
    new_line = new_line.replace('_:', ':_')
    new_line = new_line.replace('_', '[', 1)

    new_line = rreplace(new_line, '_', ']', 1)
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
    if entry.startswith(u'Secretários:'):
        return entry
    new_entry = u''
    lines = entry.split('\n')
    for line in lines:
        if ((len(line) > 60 and not line.strip().endswith(('.', ':', '?', '!'))) or
            lines.index(line) == len(lines)-1 or # last line?
            line.strip().endswith(('Sr.', 'Srs.'))
            ):
            new_entry += (line)
        else:
            new_entry += (line + '\n')
    return new_entry

def split_speaker(entry):
    parts = entry.split(u': — ', 1)
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

def find_summary(entry):
    if not u"S U M Á R I O" in entry:
        return entry
    lines = entry.split('\n')
    new_lines = []
    for line in lines:
        if line.startswith('*S U M') and line.strip().endswith('*'):
            line = u'[Sumário:]'
        new_lines.append(line)
    return '\n'.join(new_lines)

def find_special_lines(entry):
    if entry.startswith('*REUNI'):
        new_entry = entry.replace('*', '[', 1)
        new_entry = new_entry.replace('*', ']', 1)
        new_entry = new_entry.replace(u'REUNIÃO PLENÁRIA DE ', '').lower()
        return new_entry

    elif entry.startswith('*Presidente*'):
        new_entry = entry.replace('*', '')
        name = new_entry.split(':')[1]
        name = name.replace(u'Ex.ma Sr.ª', '').strip()
        return u'[Presidente:]\n%s' % name

    elif entry.startswith(u'Secretários:'):
        names = entry.split(':')[1]
        names = names.replace(u'Ex.mos Srs.', '').strip()
        return u'[Secretários:]\n%s' % names

    return entry

def parse_date_line(entry):
    pass

def apply_replaces(entry):
    for old, new in REPLACES:
        if old in entry:
            entry = entry.replace(old, new)
    return entry

source = open(sys.argv[1], 'r').read()
txt = remove_double_newlines(source)
entries = txt.split('\n\n')
parsed_entries = []
for entry in entries:
    entry = unicode(entry, 'utf-8')
    if is_irrelevant(entry):
        continue

    entry = correct_newlines(entry)
    try:
        entry = split_speaker(entry)
    except IndexError:
        print entry
        raise

    entry = fix_italics(entry)
    if is_single_italic_line(entry):
        entry = reformat_italic_line(entry)

    entry = find_summary(entry)
    entry = find_special_lines(entry)

    entry = apply_replaces(entry)

    parsed_entries.append(entry)

# second pass: find and remove rollcalls
final_entries = []
filtering_rollcall = False
for entry in parsed_entries:
    if entry.startswith((u'[Deputados presentes',
                         u'[Srs. Deputados',
                         u'[Deputados não presentes',
                         u'[Deputados que faltaram',
                         )):
        filtering_rollcall = True
        continue
    elif filtering_rollcall:
        if not '.' in entry and not ':' in entry:
            continue
        else:
            filtering_rollcall = False

    # remover restos que ficam depois de remover sumários
    if entry.strip() in ('[a]', '[b]', '[offshore]', '[outsourcing]', '[low cost]', '[A Portuguesa]',
            'post-its', u'[Diário]', 'A D R A A.') or 'A D R A A' in entry:
        continue

    final_entries.append(entry)

parsed_txt = u'\n\n'.join(final_entries)
import codecs
outfile = codecs.open(sys.argv[2], 'w', 'utf-8')
outfile.write(parsed_txt)
outfile.close()

