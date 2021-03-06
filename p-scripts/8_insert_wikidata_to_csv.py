 # Зависимости
# Python 3.8 https://www.python.org/downloads/

import re
import csv
import argparse

wikidata_table_sourcecols = ['source', 'fio_full', 'fio_short', 'wikidata', 'wikidata_url']
csv_source_cols = ['автор', 'адресат_ио', 'адресатИП']
rescols = ['auth_wikidataid','auth_wikidata_url','dest_wikidataid','dest_wikidata_url'] 

def main():

    parser = argparse.ArgumentParser(prog='Personalii convert', description='Write found wikidata ids')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                    help='csv file for processing', default="../data/muratova_res6.csv")
    parser.add_argument('infile_wikidata',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                    help='file with persons with wikidata ids', default="../data/persons_table_wikidata.csv")
    parser.add_argument('outfile', type=argparse.FileType('w', encoding='utf-8'), nargs='?',
                    help='csv file for output', default="../data/muratova_res7.csv")
    args = parser.parse_args()
    infile_data=args.infile.name
    infile_wikidata=args.infile_wikidata.name
    outfile=args.outfile.name

    ptable = []
    with open(infile_wikidata, newline='', encoding='utf-8') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        for line in reader:
            # добавляем в список
            ptable.append(line)

    with open(infile_data, newline='', encoding='utf-8') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        res_fieldnames=reader.fieldnames+rescols
        with open(outfile, "w", newline='', encoding='utf-8') as resfile:
            writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
        for line in reader:
            d=next((item for item in ptable if (
                (line["автор"] == item["source"]) or (line["автор"] == item["fio_full"]) or (line["автор"] == item["fio_short"])
                and item["wikidata_id"]
                )
                ), None)
            if d:
                line.update({rescols[0]:d['wikidata_id']})
                line.update({rescols[1]:d['wikidata_url']})


            dest = line[csv_source_cols[2]].strip()
            dest_io = ''
            if line[csv_source_cols[1]]:
                dest_io = line[csv_source_cols[1]].strip()
                dest = dest + ', ' + dest_io

            d=next((item for item in ptable if (
                (dest == item["source"]) or (dest == item["fio_full"]) or (dest == item["fio_short"])
                and item["wikidata_id"]
                )
                ), None)
            if d:
                line.update({rescols[2]:d['wikidata_id']})
                line.update({rescols[3]:d['wikidata_url']})
            with open(outfile, "a", newline='', encoding='utf-8') as resfile:
                    writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                    writer.writerow(line)


if __name__ == '__main__':
    main()