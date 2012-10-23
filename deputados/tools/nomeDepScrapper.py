#!/usr/bin/python


from urllib import urlopen
from csv import reader
from csv import writer
#from time import sleep


url_formatter='http://www.parlamento.pt/DeputadoGP/Paginas/Biografia.aspx?BID=%s'

def main():
    csv_MP=reader(open('MP.csv'),delimiter='|', quotechar='"')
    csv_short=writer(open('short_oficial.csv', 'w'), delimiter='|')
    trigger='NomeDeputado'
    for mp in csv_MP:
        mp_id=mp[1]
        print 'scrapping for id: %s' % mp_id
        uo=urlopen(url_formatter % mp_id)
        page=uo.read()
        
        offset=page.find(trigger)+len(trigger)
        init_pos = page[offset:].find(trigger)+offset+len(trigger)
        final_pos=page[init_pos:].find('<')+init_pos
        nome=page[init_pos+2:final_pos]
        if len(nome)>0 and offset>-1:
            csv_short.writerow([mp_id,nome])
            print '%s - %s' % (mp_id,nome)
        else:
            csv_short.writerow([mp_id,'N/A'])
            print '%s - %s' % (mp_id,'N/A')

if __name__ == '__main__':
    main()






