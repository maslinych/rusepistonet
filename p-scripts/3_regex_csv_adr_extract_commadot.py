# Зависимости
# Python 3.8 https://www.python.org/downloads/

import re
import csv
import argparse

sourcecol = 'адресат_имя' # Столбец со строками для обработки
rescols = ['адресат_тчкзпт'] # столбцы куда надо будет записать данные

def extract_data_person2(_celldata):
    commadot=_celldata.split(';')
    res_persons=[]
    for cd_part in commadot:
        res_persons.append( { rescols[0] : cd_part } )
    return res_persons

def main():

    parser = argparse.ArgumentParser(prog='Personalii convert', description='Extract personalies into another column and/or modify them')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                    help='csv file for processing', default="../data/muratova_res2.csv")
    parser.add_argument('outfile', type=argparse.FileType('w', encoding='utf-8'), nargs='?',
                    help='csv file for output', default="../data/muratova_res3.csv")
    args = parser.parse_args()
    infile=args.infile.name
    outfile=args.outfile.name

    with open(infile, newline='', encoding='utf-8') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        res_fieldnames=reader.fieldnames+rescols
        with open(outfile, "w", newline='', encoding='utf-8') as resfile:
            writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
        for line in reader:
            cell=line[sourcecol]
            if cell: 
                extracted_data=extract_data_person2(cell)
            else:
                extracted_data=[{ rescols[0] : "" }]
            for one_data in extracted_data:
                line.update(one_data)
                with open(outfile, "a", newline='', encoding='utf-8') as resfile:
                    writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                    writer.writerow(line)


if __name__ == '__main__':
    main()