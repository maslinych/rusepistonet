# Зависимости
# Python 3.8 https://www.python.org/downloads/

# колонка "персоналии" (адресаты) - выделяем в отдельную колонку примечение (то что в круглых или квадратных скобках)

import re
import csv
import argparse

default_source_file = '../data/muratova_res06.csv'
default_dest_file = '../data/muratova_res07.csv'
sourcecol = 'personalities_semicolon' # Столбец со строками для обработки
rescols = ['personalities_name', 'personalities_note'] # столбцы куда надо будет записать данные

def extract_data_person(_celldata):
    res_cell=re.search(r'^(.*?)([\(\[].*[\]\)])?$',_celldata, re.IGNORECASE)
    if res_cell:
        person=res_cell.group(1)
        prim=res_cell.group(2)

        if person:
            person=person.strip()
            
        if prim:
            prim=prim.strip()
            square_parentesis=re.search(r'^\[.+\]$',prim)
            prim=re.sub(r'[\(\[\]\)]','',prim)
            if square_parentesis and len(prim)>4:
                tmp=person
                person=prim
                prim=tmp

        return { rescols[0]: person, 
                rescols[1]: prim}
    else:
        return { rescols[0]:"", 
                rescols[1]: ""}


def main():

    parser = argparse.ArgumentParser(prog='Personalii convert', description='Extract personalies into another column and/or modify them')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                    help='csv file for processing', default=default_source_file)
    parser.add_argument('outfile', type=argparse.FileType('w', encoding='utf-8'), nargs='?',
                    help='csv file for output', default=default_dest_file)
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
                extracted_data=extract_data_person(cell)
            else:
                extracted_data={ rescols[0]:"", 
                rescols[1]: ""}

            line.update(extracted_data)

            with open(outfile, "a", newline='', encoding='utf-8') as resfile:
                writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                writer.writerow(line)


if __name__ == '__main__':
    main()