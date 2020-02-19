# Зависимости
# Python 3.8 https://www.python.org/downloads/
# pip install pymorphy2
# pip install -U pymorphy2-dicts-ru

import pymorphy2
from pymorphy2.shapes import restore_capitalization
import re
import logging
import csv
import argparse

# Логирование в utf-8 для отладки 
logging.basicConfig(handlers=[logging.FileHandler(r"xlwings.log", 'w', 'utf-8')], level=logging.INFO)

sourcecol = 'адресат' # Столбец со строками для обработки
rescols = ['адресат_имя', 'адресат_примечание'] # столбцы куда надо будет записать данные

def safe_list_get (l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default

def extract_data_person(_celldata):
    res_cell=re.search(r'^(.*?)( ?[\(\[].*[\]\)])?$',_celldata, re.IGNORECASE)
    if res_cell:
        person=res_cell.group(1)
        prim=res_cell.group(2)

        if person:
            person=person.strip()
            if person.endswith('.'):
                person=person[:-1]
            person=re.sub(r"\s\s+", " ", person)
        if prim:
            prim=prim.strip()
    else:
        return ["","",""]

    return [person,prim]

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
                extracted_data=["","",""]
            res_line=line
            for num,col in enumerate(rescols, start=0):
                res_line[col]=extracted_data[num]
            with open(outfile, "a", newline='', encoding='utf-8-sig') as resfile:
                writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';')
                writer.writerow(res_line)


if __name__ == '__main__':
    main()