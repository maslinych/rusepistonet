# Зависимости
# Python 3.8 https://www.python.org/downloads/


import logging
import time
import sys
import csv
import argparse


# Логирование в utf-8 для отладки
logging.basicConfig(
    handlers=[logging.StreamHandler(sys.stdout)], level=logging.INFO)

def main():
    parser = argparse.ArgumentParser(prog='Extract acad list', description='Write acad lines')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                    help='csv file for processing', default="../data/muratova_res7.csv")
    parser.add_argument('infile_acad_list',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                    help='file with persons with wikidata ids', default="../data/publications_list.txt")
    parser.add_argument('outfile', type=argparse.FileType('w', encoding='utf-8'), nargs='?',
                    help='csv file for output', default="../data/muratova_academic.csv")
    args = parser.parse_args()
    infile_data=args.infile.name
    infile_acad_list=args.infile_acad_list.name
    outfile=args.outfile.name

    ptable = []
    with open(infile_acad_list, newline='', encoding='utf-8') as datafile:
        for line in datafile:
            ptable.append(line.rstrip('\n'))

    with open(infile_data, newline='', encoding='utf-8') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        res_fieldnames=reader.fieldnames
        with open(outfile, "w", newline='', encoding='utf-8') as resfile:
            writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
        for line in reader:
            if (line["публикация"] in ptable) or (line["публикация"]=="" and line["автор"]=="Чехов, Антон Павлович"): 
                with open(outfile, "a", newline='', encoding='utf-8') as resfile:
                    writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                    writer.writerow(line)

if __name__ == '__main__':
    main()