# Зависимости
# Python 3.8 https://www.python.org/downloads/

import re
import csv
import argparse

sourcecol = 'адресат' # Столбец со строками для обработки
rescols = ['адресат_имя', 'адресат_примечание'] # столбцы куда надо будет записать данные

def extract_data_person(_celldata):
    res_cell=re.search(r'^(.*?)([\(\[].*[\]\)])?$',_celldata, re.IGNORECASE)
    if res_cell:
        person=res_cell.group(1)
        prim=res_cell.group(2)

        if person:
            person=person.strip()
            if person.endswith('.'):
                person=person[:-1]
            
        if prim:
            prim=prim.strip()

        return { rescols[0]: person, 
                rescols[1]: prim}
    else:
        return { rescols[0]:"", 
                rescols[1]: ""}


def main():

    parser = argparse.ArgumentParser(prog='Personalii convert', description='Extract personalies into another column and/or modify them')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8-sig'), nargs='?',
                    help='csv file for processing', default="../data/muratova_res.csv")
    parser.add_argument('outfile', type=argparse.FileType('w', encoding='utf-8-sig'), nargs='?',
                    help='csv file for output', default="../data/muratova_res2.csv")
    args = parser.parse_args()
    infile=args.infile.name
    outfile=args.outfile.name

    with open(infile, newline='', encoding='utf-8-sig') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        res_fieldnames=reader.fieldnames+rescols
        with open(outfile, "w", newline='', encoding='utf-8-sig') as resfile:
            writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';')
            writer.writeheader()
        for line in reader:
            cell=line[sourcecol]
            if cell: 
                extracted_data=extract_data_person(cell)
            else:
                extracted_data={ rescols[0]:"", 
                rescols[1]: ""}

            line.update(extracted_data)

            with open(outfile, "a", newline='', encoding='utf-8-sig') as resfile:
                writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';')
                writer.writerow(line)


if __name__ == '__main__':
    main()