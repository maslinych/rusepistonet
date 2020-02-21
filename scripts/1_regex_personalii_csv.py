# Зависимости
# Python 3.8 https://www.python.org/downloads/
# pip install pymorphy2
# pip install -U pymorphy2-dicts-ru русский словарь

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
    '''
    if res_cell:
        person=res_cell.group(1)
        letters_count=res_cell.group(2)
        dates=res_cell.group(3)

        if person:
            person=person.strip()
            if person.endswith('.'):
                person=person[:-1]
            person=re.sub(r"\s\s+", " ", person)
        if dates:
            dates=dates.strip()
            if re.findall(r'[.,;]$',dates):
                dates=dates[:-1]
            dates=re.sub(r"\s\s+", " ", dates)
    else:
        return ["","",""]

    return [person,letters_count,dates]

def main():

    parser = argparse.ArgumentParser(prog='Personalii convert', description='Extract personalies into another column and/or modify them')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8-sig'), nargs='?',
                    help='csv file for processing', default="../data/muratova.csv")
    parser.add_argument('outfile', type=argparse.FileType('w', encoding='utf-8-sig'), nargs='?',
                    help='csv file for output', default="../data/muratova_res.csv")
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
                extracted_data=extract_data(cell)
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