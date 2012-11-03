#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import binascii

BASE_URL_TEMPLATE = u'http://app.parlamento.pt/darpages/dardoc.aspx?doc=%s&nome=%s'

URL_TEMPLATES = {
        12: u'http://arnet/sites/XIILeg/DARI/DARIArquivo/%d.ª%%20Sessão%%20Legislativa/DAR-I-%03d.pdf',
        11: u'http://arnet/sites/XILEG/DARI/DARIArquivo/%dª%%20Sessão%%20Legislativa/DAR-I-%03d.pdf',
        10: u'http://arnet/sites/XLEG/DARI/DARIArquivo/%dª%%20Sessão%%20Legislativa/DARI%03d.pdf',
        9:  u'http://arnet/sites/IXLEG/DARI/DARIArquivo/%d.ª%%20Sessão%%20Legislativa/DARI%03d.pdf',
        8:  u'http://arnet/sites/VIIILEG/DARI/DARIArquivo/%d.ª%%20Sessão%%20Legislativa/DARI%03d.pdf',
        7:  u'http://arnet/sites/VIILEG/DARI/DARIArquivo/%d.ª%%20Sessão%%20Legislativa/DAR%03d.pdf',
        }

def encode_url(leg, sess, number):
    leg = int(leg)
    sess = int(sess)
    number = int(number)
    internal_url = URL_TEMPLATES[leg] % (sess, number)
    if leg == 12 and sess == 1:
        internal_url = internal_url.replace('.', '', 1)
    #print internal_url
    import base64
    binstring = base64.b64encode(internal_url.encode('utf8'))
    hexstring = binascii.hexlify(binstring)
    name = 'DAR-I-%03d.pdf' % int(number)
    url = BASE_URL_TEMPLATE % (hexstring, name)
    # caso especial para leg 12 e sess 1, tiramos o ponto de 1.ª para 1ª
    return url

def decode_url(url):
    hexstring = url.split('=')[1].split('&')[0]
    binstring = binascii.unhexlify(hexstring)
    internal_url = binascii.a2b_base64(binstring)
    return internal_url

if __name__ == '__main__':
    if len(sys.argv) == 2:
        url = sys.argv[1]
        print decode_url(url)
    elif len(sys.argv) == 4:
        print encode_url(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print 'Only 1 argument (URL) or 3 (legislature, leg. session, number) expected.'
        sys.exit()

