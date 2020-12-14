# Зависимости
# Python 3.8 https://www.python.org/downloads/

import re
import csv
import argparse
import sys
import logging

# Логирование в utf-8 для отладки
logging.basicConfig(
    handlers=[logging.StreamHandler(sys.stdout),logging.FileHandler(r"dedup.log", 'w', 'utf-8')], level=logging.INFO)
#
sourcecols = ['автор', 'публикация', 'год публикации', 'персоналии']
rescols = sourcecols
months = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']


def main():

    parser = argparse.ArgumentParser(prog='separation of personalities',
                                     description='Extract personalities into another column and/or modify them')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                        help='csv file for processing', default="../data/muratova.csv")
    parser.add_argument('outfile', type=argparse.FileType('w', encoding='utf-8'), nargs='?',
                        help='csv file for output', default="../data/muratova_nondups.csv")
    args = parser.parse_args()
    infile = args.infile.name
    outfile = args.outfile.name

    ptable = []
    with open(infile, newline='', encoding='utf-8') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        res_fieldnames = reader.fieldnames
        for line in reader:
            # добавляем в список
            ptable.append(line)

    logging.info(len(ptable))

    while True:
        outer_break=True
        for p in ptable:
            has_month=None
            for m in months:
                has_month=re.search(m,p['персоналии'],re.IGNORECASE)
                if has_month:
                    break
            if not has_month:
                continue
            d=next((item for item in ptable if (
                (p != item) and
                (p["автор"] == item["автор"]) and 
                (p["персоналии"] == item["персоналии"]) and 
                (p["публикация"] != item["публикация"])
                )
                ), None)
            if d:
                to_remove=None
                left=None
                right=None
                try:
                    left=int(p['год публикации']) if re.search(r'\d{4}',p['год публикации']) else None
                    right=int(d['год публикации']) if re.search(r'\d{4}',d['год публикации']) else None
                except:
                    pass
                if not (left and right):
                    continue
                if left>right:
                    to_remove=p
                elif left<right:
                    to_remove=d
                else:
                    continue
                # else:
                #     if len(p["публикация"]) > len(d["публикация"]):
                #         to_remove=d
                #     else:
                #         to_remove=p
                if to_remove:
                    outer_break=False
                    try:
                        logging.info("Comparing:")
                        logging.info(d)
                        logging.info(p)
                        logging.info("Removing:")
                        logging.info(to_remove)
                        ptable.remove(to_remove)
                        logging.info("Removed")
                    except:
                        logging.info("Removing failed")
                    #break
            # else:
            #     continue
        if outer_break:
            break

    logging.info(len(ptable))

    with open(outfile, "w", newline='', encoding='utf-8') as resfile:
        writer = csv.DictWriter(
            resfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for line in ptable:
            writer.writerow(line)


if __name__ == '__main__':
    main()
