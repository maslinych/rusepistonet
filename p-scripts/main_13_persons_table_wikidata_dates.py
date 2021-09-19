# Зависимости
# Python 3.8 https://www.python.org/downloads/
# qwikidata

# добавляем дату рождения и смерти из wikidata

import re
import logging
import time
import sys
import csv
import argparse
import datetime
from dateutil.parser import parse
from networkx.classes.function import degree
from requests import get
import hashlib
import uuid
import os

# Логирование в utf-8 для отладки
logging.basicConfig(
    handlers=[logging.StreamHandler(sys.stdout)], level=logging.INFO)

default_source_file = '../data/persons_table_res12.csv'
default_dest_file = '../data/persons_table_res13.csv'

# столбцы со строками для обработки
sourcecols = ['wikidata_id','fam_orig']

rescols = ['wikidata_birthdate', 'wikidata_enddate']


def test_tag_list(keys, tags):
    for key in keys:
        if key in tags:
            return True
    return False


def safe_list_get(l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default

def get_property_value(entity, prop_id, prop_type):
    claims = entity.get('claims')
    try:
        prop = claims.get(prop_id)[0]
        value = prop.get('mainsnak').get(
            'datavalue').get('value').get(prop_type)
        return value
    except:
        return ''


def get_year(wikidate):
    if wikidate[0] == '-':
        return ''
    elif wikidate[0] == '+':
        year = wikidate[1:5]
        return year
    else:
        return ''


ent_count=0

def select_entity(entity):
    global ent_count
    resp_code = 0
    while resp_code != 200:
        # time.sleep(1)
        logging.info(str(entity))
        resp = get('https://www.wikidata.org/w/api.php', {
            'action': 'wbgetentities',
            'ids': entity,
            'format': 'json',
            'languages': 'ru',
        })
        resp_code = resp.status_code
        if resp_code != 200:
            time.sleep(3)
            continue
        resp_json = resp.json()
        if len(resp_json.get('entities')) > 0:
            resp_entities = resp_json['entities']
            # logging.info(str(entities))
            for wid, entity in resp_entities.items():
                print(str(wid))
                print(str(entity))
                P31instanceof = get_property_value(entity, 'P31', 'id')
                P569birthdate = get_property_value(entity, 'P569', 'time')
                P570deathdate = get_property_value(entity, 'P570', 'time')
                print(str(P31instanceof))
                if not (P31instanceof in ['Q5']):
                    continue
                # print(str(P569birthdate))
                if P569birthdate:
                    birthdate = get_year(P569birthdate)
                    print(birthdate)
                else:
                    birthdate = ''
                # print(str(P570deathdate))
                if P570deathdate:
                    deathdate = get_year(P570deathdate)
                    print(deathdate)
                else:
                    deathdate = ''
                return [birthdate, deathdate]
    ent_count=ent_count+1
    return ['', '']


def main():
    global ent_count

    parser = argparse.ArgumentParser(
        prog='Wikidata search', description='Search persons in wikidata')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                        help='csv file for processing', default=default_source_file)
    parser.add_argument('outfile', type=argparse.FileType('a', encoding='utf-8'), nargs='?',
                        help='csv file for output', default=default_dest_file)
    args = parser.parse_args()
    infile = args.infile.name
    outfile = args.outfile.name

    # список словарей с персонами
    ptable = []
    if os.path.isfile(outfile):
        with open(outfile, newline='', encoding='utf-8') as datafile:
            reader = csv.DictReader(datafile, delimiter=';')
            for line in reader:
                # добавляем в список
                ptable.append(line)

    with open(infile, newline='', encoding='utf-8') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        res_fieldnames = reader.fieldnames + rescols
        for line in reader:
            # ряд для ptable
            row = line
            to_search = ''
            dup=None
            dup=next((item for item in ptable if line["source"] == item["source"]), None)
            if dup:
                continue
            if line[sourcecols[0]] and line[sourcecols[0]].startswith("Q"):
                to_search = line[sourcecols[0]]
            stopword=re.search(r'[«»]', line[sourcecols[1]])
            unknown=re.search(r'еизвес', line[sourcecols[1]])
           
            row['wikidata_birthdate'], row['wikidata_enddate'] = ['','']
            if to_search and not (stopword or unknown):
                row['wikidata_birthdate'], row['wikidata_enddate'] = select_entity(to_search)

            # добавляем в список
            ptable.append(row)

    #ptable=list({item["fio_short"]: item for item in ptable}.values())
    #ptable=sorted(ptable, key = lambda i: i['source'])

    with open(outfile, "w", newline='', encoding='utf-8') as resfile:
        writer = csv.DictWriter(
            resfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
    for line in ptable:
        with open(outfile, "a", newline='', encoding='utf-8') as resfile:
            writer = csv.DictWriter(
                resfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(line)


if __name__ == '__main__':
    main()
