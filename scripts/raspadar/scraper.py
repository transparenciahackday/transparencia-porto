#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
import os, sys
import re
import urllib, urllib2

TARGET_DIR = './html'
BASE_URL = 'http://80.251.167.40/page.aspx?cid=r3.dar&diary='
BASE_INDEX_URL = 'http://80.251.167.40/diary.aspx?cid=r3.dar&'
GET_COOKIE_URL = 'http://80.251.167.40/catalog.aspx?cid=r3.dar'

# number of sessions per legislature
SESSIONS = {12:1, 11: 2, 10: 4, 9: 3, 8: 3, 7: 4, 6: 4,
            5: 4, 4: 2, 3: 2, 2: 3, 1: 4,}

def get_page_url(leg, sess, num, pag):
    querystring = 's1l%dsl%dn%d-%04d' % (leg, sess, num, pag)
    url = BASE_URL + querystring
    return url

def get_diary_url(leg, sess, num):
    querystring = 'num=%03d&leg=l%02d&ses=sl%d' % (num, leg, sess)
    url = BASE_INDEX_URL + querystring
    return url

def get_page_range(leg, sess, num):
    url = get_diary_url(leg, sess, num)
    print url
    html = urllib.urlopen(url).read()
    soup = BeautifulSoup(html)

    rangestring = soup.find(text=re.compile('^[0-9]{4}-[0-9]{4}$'))
    if rangestring:
        start, end = rangestring.split('-') 
        return (int(start), int(end))
    else:
        print 'Diary %d does not exist (leg-%d sess-%d)' % (num, leg, sess)
        sys.exit()

def get_page(leg, sess, num, pag):
    url = get_page_url(leg, sess, num, pag)
    # we need cookie support here
    o = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    urllib2.install_opener(o)
    html = o.open(url).read()
    soup = BeautifulSoup(html)

    content = soup.findAll('body')[1].prettify() 
    return content

def get_diary(leg, sess, num):
    errors = False
    filename = 'dar_%02d_%02d_%03d.html' % (leg, sess, num)
    target = os.path.join(TARGET_DIR, filename)
    if os.path.exists(target):
        print "File %s already exists. Not scraping this one." % (target)
        return
    print 'Fetching page range...'
    start, end = get_page_range(leg, sess, num)
    page_contents = {}
    for page in range(start, end+1):
        print 'Getting page %d...' % page 
        try:
            page_contents[page] = get_page(leg, sess, num, page)
        except:
            print 'Page %d corrupted. (Leg %d, Sess %d, Number %d)' % (page, leg, sess, num)
            errors = True
            break
    f = open(target, 'wb')
    content = ''
    if errors:
        print 'Errors found, saving as empty file.'
        f.close()
        return
    for page in range(start, end+1):
        content += '\n' + page_contents[page]
    print 'Creating %s...' % filename
    f.write(content)
    f.close()


if __name__ == '__main__':
    #if len(sys.argv) != 4:
    #    print 'I need 3 arguments: <leg> <sess> <num>'
    #    sys.exit()

    from taskqueue import Queue, Task
    q = Queue()

    leg = int(sys.argv[1])
    if len(sys.argv) == 3:
        sess = int(sys.argv[2])
        for i in range(1, 200):
            q.append(Task(get_diary, args=(leg, sess, i)))
    else:
        for s in range(1, SESSIONS[leg]):
            for i in range(1, 200):
                q.append(Task(get_diary, args=(leg, s, i)))
    q.wait()
    q.die()
