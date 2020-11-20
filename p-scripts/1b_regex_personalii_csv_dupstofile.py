# Зависимости
# Python 3.8 https://www.python.org/downloads/

import re
import csv
import argparse
import hashlib


sourcecol = 'персоналии'  # столбец со строками для обработки
# столбцы, куда надо будет записать данные
rescols = ['адресат', 'количество писем', 'даты']
sourceidcol = ['автор', sourcecol]
residcol = 'id_переписки'


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
    hash_obj = hashlib.sha1(_input_str.encode())
    return hash_obj.hexdigest()


def main():

    parser = argparse.ArgumentParser(prog='separation of personalities',
                                     description='Extract personalities into another column and/or modify them')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                        help='csv file for processing', default="../data/muratova.csv")
    parser.add_argument('outfile', type=argparse.FileType('w', encoding='utf-8'), nargs='?',
                        help='csv file for output', default="../data/muratova_res.csv")
    parser.add_argument('dupsfile', type=argparse.FileType('w', encoding='utf-8'), nargs='?',
                        help='csv file for dups', default="../data/mail_dups.csv")
    args = parser.parse_args()
    infile = args.infile.name
    outfile = args.outfile.name
    dupsfile = args.dupsfile.name

    hashes = []
    hashes_dup_printed = []
    alldata = []
    with open(infile, newline='', encoding='utf-8') as datafile:
        # newline='' - для корректного определения новой строки
        reader = csv.DictReader(datafile, delimiter=';')
        res_fieldnames = [residcol]+reader.fieldnames+rescols
        with open(outfile, "w", newline='', encoding='utf-8') as resfile:
            writer = csv.DictWriter(
                resfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()

        with open(dupsfile, "w", newline='', encoding='utf-8') as cdupsfile:
            writer = csv.DictWriter(
                cdupsfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
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
            line.update({residcol: idres})

            with open(outfile, "a", newline='', encoding='utf-8') as resfile:
                writer = csv.DictWriter(
                    resfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                writer.writerow(line)

            if (idres in hashes):
                if not idres in hashes_dup_printed:
                    d=next((item for item in alldata if (idres == item[residcol])), None)
                    if not d:
                        exit(1)
                    hashes_dup_printed.append(idres)
                    with open(dupsfile, "a", newline='', encoding='utf-8') as cdupsfile:
                        writer = csv.DictWriter(
                            cdupsfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                        writer.writerow(d)

                with open(dupsfile, "a", newline='', encoding='utf-8') as cdupsfile:
                    writer = csv.DictWriter(
                        cdupsfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                    writer.writerow(line)

            alldata.append(line)
            hashes.append(idres)


if __name__ == '__main__':
    main()
