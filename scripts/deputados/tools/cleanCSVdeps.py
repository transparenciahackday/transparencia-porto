import csv

datasets='../../datasets/'
csvin=datasets+'deputados_old.csv'
csvout=datasets+'deputados.csv'
csvreader=csv.reader(open(csvin), delimiter='|')
csvwriter=csv.writer(open(csvout, 'w'))

for row in csvreader:
    csvwriter.writerow([int(row[1]),
                        row[2],
                        row[5]])



