#!/usr/bin/python


from urllib import urlretrieve
from csv import reader
from csv import writer
#from time import sleep


pic_url_formatter='http://app.parlamento.pt/webutils/getimage.aspx?id=%s&type=deputado'
dest='imgs/'

def main():
    csv_MP=reader(open('MP.csv'),delimiter='|', quotechar='"')
    
    for mp in csv_MP:
        mp_id=mp[1]
        urlretrieve(pic_url_formatter % mp_id, '%s%s.jpg' % (dest,mp_id))
        print 'retrieving picture with id: %s' % mp_id
    
    print "it's almost done"
    print 'do find ./imgs/ -size -722c -exec rm {} \;'
    print 'to clean up things'
if __name__ == '__main__':
    main()






