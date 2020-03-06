# Зависимости
# Python 3.8 https://www.python.org/downloads/

import re
import csv
import argparse

replacement = {
    r'A\.':'А.',
    r'B\.':'В.',
    r'C\.':'С.',
    r'E\.':'Е.',
    r'H\.':'Н.',
    r'K\.':'К.',
    r'M\.':'М.',
    r'O\.':'О.',
    r'P\.':'Р.',
    r'T\.':'Т.',
    r'X\.':'Х.',
    r'т\. Х\.':'т. X.'
}


def replace_lat_rus(_celldata):
    for key, value in replacement.items():
        _celldata=re.sub(r" {}".format(key)," {}".format(value),_celldata)
        _celldata=re.sub(r"^{}".format(key),"{}".format(value),_celldata)
    _celldata=re.sub(r'(?:(?<!Вып\.)(?<!вып\.)(?<!кн\.) 3\.) ([А-ЯЁ][а-яё\-]+)', r' З. \1', _celldata)
    return _celldata


def main():

    parser = argparse.ArgumentParser(prog='Personalii convert', description='Extract personalies into another column and/or modify them')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8-sig'), nargs='?',
                    help='csv file for processing', default="../data/muratova.csv")
    parser.add_argument('outfile', type=argparse.FileType('w', encoding='utf-8-sig'), nargs='?',
                    help='csv file for output', default="../data/muratova_ru.csv")
    args = parser.parse_args()
    infile=args.infile.name
    outfile=args.outfile.name

    with open(infile, newline='', encoding='utf-8-sig') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        res_fieldnames=reader.fieldnames
        with open(outfile, "w", newline='', encoding='utf-8-sig') as resfile:
            writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';')
            writer.writeheader()
        for line in reader:
            for cell_name,cell_value in line.items():
                res_cell=replace_lat_rus(cell_value)
                line.update({cell_name:res_cell})
            with open(outfile, "a", newline='', encoding='utf-8-sig') as resfile:
                writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';')
                writer.writerow(line)


if __name__ == '__main__':
    main()