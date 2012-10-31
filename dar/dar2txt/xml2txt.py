#!/usr/bin/env python
# see prettify_dar.xml for a prettified xml tree
import sys
from BeautifulSoup import BeautifulStoneSoup

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
        textlines = textbox.findAll('textline')
        for textline in textlines:
            line = ''
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
            txt += line + '\n'

import codecs
outfile = codecs.open(sys.argv[2], 'w', 'utf-8')
outfile.write(txt)
outfile.close()


