#!/usr/bin/env python
from darpdfurls import encode_url
import sys, os

def dar_exists(leg, sess, num):
    url = encode_url(leg, sess, num)
    # Now we check if there's anything at the URL.
    # We always get return code 200 since there's a HTML error message, 
    # so we check if we're getting a PDF file or a HTML response.
    from urllib2 import urlopen
    response = urlopen(url)
    mimetype = response.info().values()[-1].split(';')[0]

    if mimetype == 'application/pdf':
        return True
        print "Resource exists!"
    elif mimetype == 'text/html':
        return False
    else:
        print mimetype
        raise ValueError

if __name__ == '__main__':
    if not len(sys.argv) == 4:
        print 'Give me 3 args (leg, session, number)'
        sys.exit()

    leg, sess, num = sys.argv[1:]
    if dar_exists(leg, sess, num):
        print "Resource exists!"
    else:
        print "Resource does not exist."


