#!/usr/bin/env python
# see prettify_dar.xml for a prettified xml tree
import sys
from BeautifulSoup import BeautifulStoneSoup

def bbox_coords(value):
    # these might be in the wrong order, but it's indeed xyxy order
    left, bottom, right, top = [float(x) for x in value.split(',')]
    return (left, bottom, right, top)

xml = open(sys.argv[1], 'r')
soup = BeautifulStoneSoup(xml)

pagestag = soup.findAll('pages')
assert len(pagestag) == 1
pages = pagestag[0].findAll('page')
# we'll store the output here
txt = ''
for page in pages:
    textboxes = page.findAll('textbox')
    for textbox in textboxes:
        # check textbox positioning for header filtering
        left, bottom, right, top = bbox_coords(textbox.get('bbox'))
        if page['id'] != "1" and (top > 800 or (page['id'] == "2" and top > 760)):
            continue
        # we'll store tuples for storing the text and position, since sometimes PDFminer
        # gets the word order wrong -- FIXME NOT WORKING
        textlines = []
        for textline in textbox.findAll('textline'):
            line = ''
            left_pos = bbox_coords(textline.get('bbox'))[0]
            textbits = textline.findAll('text')
            for textbit in textbits:
                if not textbit.text:
                    # check for non-breaking spaces since they happen, 
                    # for this we check for the font attribute
                    if not textbit.get('font'):
                        continue
                    # avoid double spaces, only output if last char wasn't a space
                    if line and not line[-1] == ' ':
                        line += ' '
                else:
                    # add the text to the line string, and mark it up if necessary
                    if 'Italic' in textbit['font']:
                        # remove last emphasis marker, watching for spaces
                        if line.endswith('_ '):
                            line = line[:-2] + ' ' + textbit.text + '_'
                        elif line.endswith('_'):
                            line = line[:-1] + textbit.text + '_'
                        else:
                            line += '_' + textbit.text + '_'
                    elif 'Bold' in textbit['font']:
                        # remove last strong marker, watching for spaces
                        if line.endswith('* '):
                            line = line[:-2] + ' ' + textbit.text + '*'
                        elif line.endswith('*'):
                            line = line[:-1] + textbit.text + '*'
                        else:
                            line += '*' + textbit.text + '*'
                    else:
                        line += textbit.text
            textlines.append((left_pos, line))
        # sort list by position 
        # NOT working, it mixes lines in different heights....
        # sorted_lines = sorted(textlines, key=lambda tup: tup[0])
        sorted_lines = textlines

        for pos, line in sorted_lines:
            txt += line + '\n'

import codecs
outfile = codecs.open(sys.argv[2], 'w', 'utf-8')
outfile.write(txt)
outfile.close()


