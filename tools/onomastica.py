#!/usr/bin/python
# -*- coding: utf-8 -*-
# Pedro Rodrigues - medecau.com - medecau@gmail.com
from urllib import urlopen
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
from string import translate
from csv import writer
'''

Mais info:
http://www.pinkblue.com/nomes/desc.asp?id=449
http://babynamesworld.parentsconnect.com/profile.php?name=Pedro
http://www.babynames.com/Names/search.php?searchby=byname&searchterm=Pedro

'''

base_path='http://ferrao.org/onomastica/'
pagina_inicial='node3cd97.html'

page=urlopen(base_path+pagina_inicial).read()

page=page.decode('utf-8')

soup = BeautifulSoup(page)

primeira_table=soup.body.form.div.table
alfabeto_div=primeira_table.contents[1].td.div

alfabeto={}

for each in alfabeto_div:
    try:
        alfabeto[each.a.string]=each.a['href']
    except:
        pass

csv_writer=writer(open('genero.csv', 'w'))

for letter, page in alfabeto.iteritems():
    page= urlopen(base_path+page).read()
    page=page.decode('utf-8')
    soup = BeautifulSoup(page)
    names_tr=soup.html.body.form.contents[6].tr
    for each_td in names_tr:
        for each in each_td:
            new_row=[]
            try:
                if each.name=='a':
                    new_row.append(BeautifulStoneSoup(each.string, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).encode('utf-8'))
                    
                    if each['style'].find('#ff6790')>-1:
                        new_row.append('F')
                    elif each['style'].find('#0097ff')>-1:
                        new_row.append('M')
                    else:
                        new_row.append('')
                    
                    csv_writer.writerow(new_row)
            except:
                pass




