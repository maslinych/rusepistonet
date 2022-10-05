# Зависимости
# Python 3.8 https://www.python.org/downloads/

# колонка "персоналии" (адресаты) - разделяем на отдельные строки каждого автора письма (если их несколько), разделенных ';' (точкой с запятой)

import re
import csv
import argparse

default_source_file = '../data/muratova_res05.csv'
default_dest_file = '../data/muratova_res06.csv'
sourcecol = 'personalities_dest' # Столбец со строками для обработки
numcol = 'letter_number'
rescols = ['personalities_semicolon'] # столбцы куда надо будет записать данные

def extract_data_person2(_celldata):
    commadot=_celldata.split(';')
    res_persons=[]
    skob_open=False
    string_collect=""
    for cd_part in commadot:
        if (re.search("\(.+\)", cd_part) or not re.search("\(",cd_part)) and not skob_open:
            res_persons.append( { rescols[0] : cd_part.strip() } )
        elif re.search("\(",cd_part):
            skob_open = True
            string_collect=""
            string_collect=cd_part+";"
        elif skob_open and not re.search("\)",cd_part.strip()):
            string_collect=string_collect+" "+cd_part
        elif skob_open and re.search("\)",cd_part.strip()):
            skob_open = False
            string_collect=string_collect+" "+cd_part
            res_persons.append( { rescols[0] : string_collect.strip() } )
            string_collect = ""
    return res_persons

def main():

    parser = argparse.ArgumentParser(prog='Personalii convert', description='Extract personalies into another column and/or modify them')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                    help='csv file for processing', default=default_source_file)
    parser.add_argument('outfile', type=argparse.FileType('w', encoding='utf-8'), nargs='?',
                    help='csv file for output', default=default_dest_file)
    args = parser.parse_args()
    infile=args.infile.name
    outfile=args.outfile.name

    parsed_letters = {}
    with open(infile, newline='', encoding='utf-8') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        res_fieldnames=reader.fieldnames+rescols
        with open(outfile, "w", newline='', encoding='utf-8') as resfile:
            writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
        for line in reader:
            if not line[numcol] in parsed_letters:
                cell=line[sourcecol]
                if cell: 
                    extracted_data=extract_data_person2(cell)
                else:
                    extracted_data=[{ rescols[0] : "" }]
                parsed_letters[line[numcol]] = extracted_data
            else:
                extracted_data = parsed_letters[line[numcol]]
            for one_data in extracted_data:
                line.update(one_data)
                with open(outfile, "a", newline='', encoding='utf-8') as resfile:
                    writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                    writer.writerow(line)


if __name__ == '__main__':
    main()