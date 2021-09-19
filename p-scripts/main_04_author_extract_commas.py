# Зависимости
# Python 3.8 https://www.python.org/downloads/

# колонка автор - разделяем на отдельные строки персоналии, разделенные запятой

import re
import csv
import argparse

default_source_file = '../data/muratova_res03.csv'
default_dest_file = '../data/muratova_res04.csv'
sourcecol = 'автор_тчкзпт' # Столбец со строками для обработки
rescols = ['автор_одиночн'] # столбцы куда надо будет записать данные

def extract_data_person2(_celldata):
    res_persons=[]
    innerparts=_celldata.split(',')
    rightparts=innerparts[-1].strip().split(' ')
    if len(rightparts)>3 and not( '.' in ' '.join(innerparts[:-1])):
        # not( '.' in ' '.join(innerparts[:-1]))): -  for  'В. И. Баксту, другим организаторам Гейдельбергской читальни'
        res_persons.append(_celldata)
        return res_persons
    if '.,' in _celldata:
        lio=rightparts[:-1]
        lfam=rightparts[-1]
        io_parts=innerparts[:-1]+[' '.join(lio)]
        for in_part in io_parts:
            res_persons.append((in_part.strip()+' '+lfam).strip())
    else:
        for in_part in innerparts:
            res_persons.append((in_part.strip()).strip())
    return res_persons

def main():

    parser = argparse.ArgumentParser(prog='Personalii convert', description='Extract personalies into another column and/or modify them')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                    help='csv file for processing', default="../data/muratova_res3.csv")
    parser.add_argument('outfile', type=argparse.FileType('w', encoding='utf-8'), nargs='?',
                    help='csv file for output', default="../data/muratova_res4.csv")
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
                extracted_data=[""]
            for one_data in extracted_data:
                line.update({rescols[0]:one_data})
                with open(outfile, "a", newline='', encoding='utf-8') as resfile:
                    writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                    writer.writerow(line)


if __name__ == '__main__':
    main()