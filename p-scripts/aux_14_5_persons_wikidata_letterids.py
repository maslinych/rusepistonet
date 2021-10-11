# Зависимости
# Python 3.8 https://www.python.org/downloads/

# создаем таблицу с персоналиями (ФИО +  дополнительные сведения), wikidataid и wikidata url, номера писем в общем списке

import re
import csv
import argparse

default_source_file = '../data/muratova_res14.csv'
#default_persons_file = '../data/persons_table_res13.csv'
default_dest_file = '../data/persons_table_for_clearup_14_5.csv'

#wikidata_table_sourcecols = ['source', 'fio_full', 'fio_short', 'wikidata', 'wikidata_url']
csv_source_cols = ['номер в списке', 'автор_имя', 'автор_примечание', 'auth_wikidataid', 'auth_wikidata_url',
                   'адресат_ио', 'адресатИП', 'адресат_примечание', 'dest_wikidataid', 'dest_wikidata_url']
rescols = ['name', 'additional', 'wikidataid',
           'wikidata_url', 'letters_strings_num']


def main():

    parser = argparse.ArgumentParser(
        prog='Personalii', description='Write persons for tast')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                        help='csv file for processing', default=default_source_file)
    parser.add_argument('outfile', type=argparse.FileType('w', encoding='utf-8'), nargs='?',
                        help='csv file for output', default=default_dest_file)
    args = parser.parse_args()
    infile_data = args.infile.name
    outfile = args.outfile.name

    ptable = []

    with open(infile_data, newline='', encoding='utf-8') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        for line in reader:
            row = {}
            d = next((item for item in ptable if (
                (line["auth_wikidataid"] == item["wikidataid"])
            )
            ), None)

            if d:
                d.update({'letters_strings_num': ','.join(
                    (d['letters_strings_num'], line['номер в списке'].lstrip("0")))})
            else:
                row[rescols[0]] = line[csv_source_cols[1]]
                row[rescols[1]] = line[csv_source_cols[2]]
                row[rescols[2]] = line[csv_source_cols[3]]
                row[rescols[3]] = line[csv_source_cols[4]]
                row[rescols[4]] = line[csv_source_cols[0]].lstrip("0")
                ptable.append(row)

            row = {}
            d = next((item for item in ptable if (
                (line["dest_wikidataid"] == item["wikidataid"])
            )
            ), None)

            if d:
                d.update({'letters_strings_num': ','.join(
                    (d['letters_strings_num'], line['номер в списке'].lstrip("0")))})
            else:
                dst_io = [line[csv_source_cols[6]], line[csv_source_cols[5]]]
                row[rescols[0]] = ', '.join(x for x in dst_io if x)
                row[rescols[1]] = line[csv_source_cols[7]]
                row[rescols[2]] = line[csv_source_cols[8]]
                row[rescols[3]] = line[csv_source_cols[9]]
                row[rescols[4]] = line[csv_source_cols[0]].lstrip("0")
                ptable.append(row)

    with open(outfile, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(
            outfile, fieldnames=rescols, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for row in ptable:
            writer.writerow(row)


if __name__ == '__main__':
    main()
