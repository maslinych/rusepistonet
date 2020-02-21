# Зависимости
# Python 3.8 https://www.python.org/downloads/
# pip install pymorphy2
# pip install -U pymorphy2-dicts-ru

import re
import csv
import argparse

sourcecol = 'адресат_тчкзпт' # Столбец со строками для обработки
rescols = ['адресат_одиночн'] # столбцы куда надо будет записать данные

def safe_list_get (l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default

def extract_data_person2(_celldata):
    res_persons=[]
    innerparts=_celldata.split(',')
    rightparts=innerparts[-1].strip().split(' ')
    if len(rightparts)>3:
        res_persons.append(_celldata)
        return res_persons
    if '.,' in _celldata:
        lio=innerparts[-1].strip().split(' ')[:-1]
        lfam=innerparts[-1].strip().split(' ')[-1]
        io_parts=innerparts[:-1]+[' '.join(lio)]
        for in_part in io_parts:
            res_persons.append(' '.join([in_part.strip(),lfam]))
    else:
        for in_part in innerparts:
            res_persons.append(in_part)
    return res_persons

def main():

    parser = argparse.ArgumentParser(prog='Personalii convert', description='Extract personalies into another column and/or modify them')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8-sig'), nargs='?',
                    help='csv file for processing', default="../data/muratova_res3.csv")
    parser.add_argument('outfile', type=argparse.FileType('w', encoding='utf-8-sig'), nargs='?',
                    help='csv file for output', default="../data/muratova_res4.csv")
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
                extracted_data=extract_data_person2(cell)
            else:
                extracted_data=[""]
            res_line=line
            for one_data in extracted_data:
                for num,col in enumerate(rescols, start=0):
                    res_line[col]=one_data
                with open(outfile, "a", newline='', encoding='utf-8-sig') as resfile:
                    writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';')
                    writer.writerow(res_line)


if __name__ == '__main__':
    main()