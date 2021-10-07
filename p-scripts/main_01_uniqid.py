# Зависимости
# Python 3.8 https://www.python.org/downloads/

# добавляем колонки "номер переписки" (порядоковый номер письма в списке) и
# id_переписки - содержит хеш с солью (для уникальности) строки "автор + адресаты"

import re
import csv
import argparse
import hashlib
import uuid

default_source_file = '../data/muratova.csv'
default_dest_file = '../data/muratova_res01.csv'
sourcecol = 'персоналии'  # столбец со строками для обработки
# столбцы, куда надо будет записать данные
rescols = ['адресат', 'количество писем', 'даты']
sourceidcol = ['автор', sourcecol]
residcol = 'id_переписки'
rescountcol = 'номер в списке'

counter = 0


def extract_data(_celldata):
    res_cell = re.search(
        r'^(.*)\. \(([ 0-9?><]*)\)\. (.*)\.$', _celldata, re.IGNORECASE)
    '''
    r - оставляет строку без обработки
    ^ - начало строки 
    .* - любое количество любых символов
    re.IGNORECASE - флаг, игнорирование регистра
    '''
    try:
        adr = res_cell.group(1)
    except:
        print(_celldata)
        adr = ''
        res_cell = ''

    if re.search(r'\w\. \w$', adr):
        adr = adr+'.'
    if res_cell:
        return {rescols[0]: adr,
                rescols[1]: res_cell.group(2),
                rescols[2]: res_cell.group(3)}
    else:
        return {rescols[0]: "",
                rescols[1]: "",
                rescols[2]: ""}


def generate_string_id(_input_str):
    global counter
    salt = uuid.uuid4().hex
    hash_obj = hashlib.sha1(salt.encode()+_input_str.encode())
    return hash_obj.hexdigest()


def count_all():
    global counter
    counter = counter + 1
    return str(counter).zfill(10)


def main():

    parser = argparse.ArgumentParser(prog='separation of personalities',
                                     description='Extract personalities into another column and/or modify them')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                        help='csv file for processing', default=default_source_file)
    parser.add_argument('outfile', type=argparse.FileType('w', encoding='utf-8'), nargs='?',
                        help='csv file for output', default=default_dest_file)

    args = parser.parse_args()
    infile = args.infile.name
    outfile = args.outfile.name

    with open(infile, encoding='utf-8', newline='') as datafile:
        # newline='' - для корректного определения новой строки
        reader = csv.DictReader(datafile, delimiter=';')
        res_fieldnames = [rescountcol, residcol]+reader.fieldnames+rescols
        with open(outfile, "w", newline='', encoding='utf-8') as resfile:
            writer = csv.DictWriter(
                resfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()

        for line in reader:
            cell = line[sourcecol]
            if cell:
                extracted_data = extract_data(cell)
            else:
                extracted_data = {rescols[0]: "",
                                  rescols[1]: "",
                                  rescols[2]: ""}

            line.update(extracted_data)

            idsource = ''
            for p in sourceidcol:
                idsource = ":" + idsource + line[p]

            idres = generate_string_id(idsource)
            line.update({rescountcol: count_all(), residcol: idres})

            with open(outfile, "a", newline='', encoding='utf-8') as resfile:
                writer = csv.DictWriter(
                    resfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                writer.writerow(line)


if __name__ == '__main__':
    main()
