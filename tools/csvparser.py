#!/usr/bin/python
from csv import reader
from optparse import OptionParser

VERSION=0.0

class ArgParser(OptionParser):
    usage='%prog [-t] file'
    version='%prog ' + str(VERSION)

def main():
    parser=ArgParser()
    #parser.add_option('-t','--test',action='store_true')
    parser.add_option('-v','--version', action='store_true', help='')
    (options, args)=parser.parse_args()
    if options.version:
        print 'csvparser.py %s' % VERSION
    elif len(args)==1:
        print 'opening %s...' % args[0]
        csv_reader = reader(open(args[0],'r'), delimiter='|')
        fields_per_row={}
        field_length_collum={}
        for row in csv_reader:
            try:
                fields_per_row[str(len(row))]+=1
            except:
                fields_per_row[str(len(row))]=1
            for collum, field in enumerate(row):
                try:
                    field_length_collum[str(collum)][str(len(field))]+=1
                except:
                    try:
                        field_length_collum[str(collum)][str(len(field))]=1
                    except:
                        field_length_collum[str(collum)]={}
                        field_length_collum[str(collum)][str(len(field))]=1
                        
                
        for num_fields, num_rows in fields_per_row.iteritems():
            print '%s rows with %s fields' % (num_rows, num_fields)
        for collum_num, collum in field_length_collum.iteritems():
            print 'for collum %s' % collum_num
            for num_fields, num_rows in collum.iteritems():
                print '%s fields of %s length' % (num_rows, num_fields)
    else:
        print "something's wrong whith you, seek --help"
    

if __name__ == '__main__':
    main()

