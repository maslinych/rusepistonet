# Зависимости
# Python 3.8 https://www.python.org/downloads/

import re
import csv
import argparse

sourcecol = 'адресат_одиночн' # Столбец со строками для обработки
rescols = ['адресат_ио','фамилия_неделимо'] # столбцы куда надо будет записать данные

def extract_data_person(_celldata):
    search=[]
    return_value={ rescols[0]:"", rescols[1]: ""}
    search.append(re.search(r'^(?P<IO>[А-ЯЁ][а-яё\-]*?\. [А-ЯЁ][а-яё\-]*?\. [А-ЯЁ][а-яё\-]*?\.) (?P<FAM>[А-ЯЁ][А-ЯЁа-яё\-]+)$',_celldata)) # I.O.O. Fam
    search.append(re.search(r'^(?P<IO>[А-ЯЁ][а-яё\-]*?\. [А-ЯЁ][а-яё\-]*?\.) (?P<FAM>[А-ЯЁ][А-ЯЁа-яё\-]+)$',_celldata)) # I. O. Fam
    search.append(re.search(r'^(?P<IO>[А-ЯЁ][а-яё\-]*?\.-[А-ЯЁ][а-яё\-]*?\.) (?P<FAM>[А-ЯЁ][А-ЯЁа-яё\-]+)$',_celldata)) # I.-O. Fam
    search.append(re.search(r'^(?P<IO>[А-ЯЁ][а-яё\-]*? [А-ЯЁ][а-яё\-]*?\.) (?P<FAM>[А-ЯЁ][А-ЯЁа-яё\-]+)$',_celldata)) # Fullname O. Fam
    search.append(re.search(r'^(?P<IO>.*? де) (?P<FAM>[А-ЯЁ][А-ЯЁа-яё\-]+)$',_celldata)) # Fullname де Fam // Гюи де Мопассану
    search.append(re.search(r'^(?P<IO>.*? фон) (?P<FAM>[А-ЯЁ][А-ЯЁа-яё\-]+)$',_celldata)) # I. фон Fam // К. фон Полю
    search.append(re.search(r'^(?P<IO>.*? фон-дер) (?P<FAM>[А-ЯЁ][А-ЯЁа-яё\-]+)$',_celldata)) # I. фон-дер Fam // А. Ф. фон-дер Бригену
    search.append(re.search(r'^(?P<IO>[А-ЯЁ][а-яё\-]*?\.) (?P<FAM>[А-ЯЁ][А-ЯЁа-яё\-]+)$',_celldata)) # I. Fam
    search.append(re.search(r'^(?P<IO>[А-ЯЁ][а-яё\-]*?\. [А-ЯЁ][а-яё\-]*?\.)$',_celldata)) # I. O.
    search.append(re.search(r'^(?P<IO>[А-ЯЁ][а-яё\-]*?\. [А-ЯЁ][а-яё\-]*?\. [А-ЯЁ][а-яё\-]*?\.)$',_celldata)) # I. O. O.
    search.append(re.search(r'^(?P<IO>[A-Z]\. [A-Z]\.)$',_celldata)) # N. N.
    search.append(re.search(r'^(?P<IO>\?)$',_celldata)) # ? , just ?
    search.append(re.search(r'^(?P<FAM>[А-ЯЁ][а-яё\-]+)$',_celldata)) # Fam
    res_search=None
    for s in search:
        if s:
            res_search=s.groupdict()
            break
    
    if res_search:
        person_io=res_search.get('IO')
        other_part=res_search.get('FAM')

        if person_io:
            return_value[rescols[0]]=person_io.strip()
            
        if other_part:
            return_value[rescols[1]]=other_part.strip()
    else:
         return_value[rescols[1]]=_celldata.strip()
    return return_value


def main():

    parser = argparse.ArgumentParser(prog='Personalii convert', description='Extract personalies into another column and/or modify them')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                    help='csv file for processing', default="../data/muratova_res4.csv")
    parser.add_argument('outfile', type=argparse.FileType('w', encoding='utf-8'), nargs='?',
                    help='csv file for output', default="../data/muratova_res5.csv")
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