# Зависимости
# Python 3.8 https://www.python.org/downloads/

import re
import csv
import argparse


sourcecol = 'персоналии' # столбец со строками для обработки
rescols = ['адресат', 'количество писем', 'даты'] # столбцы, куда надо будет записать данные


def extract_data(_celldata):
    res_cell=re.search(r'^(.*)\. \(([ 0-9?><]*)\)\. (.*)\.$',_celldata, re.IGNORECASE) 
    '''
    r - оставляет строку без обработки
    ^ - начало строки 
    .* - любое количество любых символов
    re.IGNORECASE - флаг, игнорирование регистра
    '''
    try:
        adr=res_cell.group(1)
    except:
        print(_celldata)
        adr=''
        res_cell=''

    if re.search(r'\w\. \w$',adr):
        adr=adr+'.'
    if res_cell:
        return { rescols[0]: adr, 
                rescols[1]: res_cell.group(2),
                rescols[2]: res_cell.group(3) }
    else:
        return { rescols[0]:"", 
                rescols[1]: "",
                rescols[2]: "" }


def main():

    parser = argparse.ArgumentParser(prog='separation of personalities', description='Extract personalities into another column and/or modify them')
    parser.add_argument('infile',  type =argparse.FileType('r', encoding='utf-8-sig'), nargs='?',
                    help='csv file for processing', default="../data/muratova.csv")
    parser.add_argument('outfile', type=argparse.FileType('w', encoding='utf-8-sig'), nargs='?',
                    help='csv file for output', default="../data/muratova_res.csv")
    args = parser.parse_args()
    infile=args.infile.name
    outfile=args.outfile.name

    with open(infile, newline='', encoding='utf-8-sig') as datafile: 
        # newline='' - для корректного определения новой строки
        reader = csv.DictReader(datafile, delimiter=';')
        res_fieldnames=reader.fieldnames+rescols
        with open(outfile, "w", newline='', encoding='utf-8-sig') as resfile:
            writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';')
            writer.writeheader()
        for line in reader:
            cell=line[sourcecol]
            if cell: 
                extracted_data=extract_data(cell)
            else:
                extracted_data={ rescols[0]:"", 
                rescols[1]: "",
                rescols[2]: "" }

            line.update(extracted_data)

            with open(outfile, "a", newline='', encoding='utf-8-sig') as resfile:
                writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';')
                writer.writerow(line)


if __name__ == '__main__':
    main()