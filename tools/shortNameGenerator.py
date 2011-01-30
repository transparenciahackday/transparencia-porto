#!/usr/bin/python


from urllib import urlopen
from csv import reader
from csv import writer
#from time import sleep


url_formatter='http://www.parlamento.pt/DeputadoGP/Paginas/Biografia.aspx?BID=%s'


def prim_ultim(nome):
    first_space=nome.find(' ')
    last_space=nome.rfind(' ')
    return nome[:first_space]+nome[last_space:]

def main():
    csv_MP=reader(open('MP.csv'),delimiter='|', quotechar='"')
    csv_short_name=writer(open('short.csv', 'w'), delimiter='|')
    for mp in csv_MP:
        mp_id=mp[1]
        mp_nome=mp[2]
        if mp_nome != 'N/A':
            csv_short_name.writerow([mp_id, prim_ultim(mp_nome)])

if __name__ == '__main__':
    main()






