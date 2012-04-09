#!/usr/bin/python

import sys, os
from urllib import urlretrieve
import json
#from csv import reader
#from csv import writer
#from time import sleep

mp_file = '/home/rlafuente/proj/thd/datasets/deputados.json'
pic_url_formatter='http://app.parlamento.pt/webutils/getimage.aspx?id=%s&type=deputado'
dest='imgs/'

def main():
    if not os.path.exists(dest):
        os.mkdir(dest)
        print "Directory 'imgs/' created."

    # csv_MP=reader(open('MP.csv'),delimiter='|', quotechar='"')
    mp_json = json.loads(open(mp_file, 'r').read())
    for mp_id in mp_json:
        print 'retrieving picture with id: %s' % mp_id
        urlretrieve(pic_url_formatter % mp_id, '%s%s.jpg' % (dest,mp_id))
    
    print "it's almost done"
    print 'do find ./imgs/ -size -722c -exec rm {} \;'
    print 'to clean up things'

if __name__ == '__main__':
    main()






