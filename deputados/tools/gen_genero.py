#!/usr/bin/python
from csv import reader
from csv import writer

def main():
    csv_generos=reader(open('genero.csv'))
    csv_MP=reader(open('MP.csv'),delimiter='|', quotechar='"')
    
    list_nomes_femininos=[]
    list_nomes_masculinos=[]
    for nome in csv_generos:
        if nome[1]=='F':
            list_nomes_femininos.append(nome[0].lower())
        elif nome[1]=='M':
            list_nomes_masculinos.append(nome[0].lower())
    
    csv_genero=writer(open('mp_genero.csv', 'w'), delimiter='|')
    for mp in csv_MP:
        mp_id=mp[1]
        nome=mp[2]
        if nome.find(' ')>-1 and len(nome)>0:
            nome= nome[:nome.find(' ')]
            if nome.lower() in list_nomes_femininos:
                csv_genero.writerow([mp_id, 'F'])
            elif nome.lower() in list_nomes_masculinos:
                csv_genero.writerow([mp_id, 'M'])
            else:
                csv_genero.writerow([mp_id, ''])

if __name__ == '__main__':
    main()

