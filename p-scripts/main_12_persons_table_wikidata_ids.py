# Зависимости
# Python 3.8 https://www.python.org/downloads/
# qwikidata

# пытаемся найти id в wikidata для персоналий
# если не найдено - записываем случайный уникальный идентификатор

import re
import logging
import time
import sys
import csv
import argparse
#import datetime
from dateutil.parser import parse
from requests import get
import hashlib
import uuid
import os

# Логирование в utf-8 для отладки
logging.basicConfig(
    handlers=[logging.StreamHandler(sys.stdout)], level=logging.INFO)

default_source_file = '../data/persons_table_res11.csv'
default_dest_file = '../data/persons_table_res12.csv'

# столбцы со строками для обработки
sourcecols = ['fio_full', 'fio_short', 'fam_orig', 'io_short']

rescols = ['wikidata_id', 'wikidata_url']

bstartdate = 1750
benddate = 1900
dstartdate = 1800
denddate = 1940

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

def generate_string_id(_input):
    salt = uuid.uuid4().hex
    hash_obj = hashlib.sha1(salt.encode()+str(_input).encode())
    return hash_obj.hexdigest()

def get_qnumbers(search):

    resp_code = 0
    while resp_code != 200:
        # time.sleep(1)
        logging.info(str(search))
        resp = get('https://www.wikidata.org/w/api.php', {
            'action': 'query',
            'list': 'search',
            'srsearch': search,
            'format': 'json',
            'indexpageids': '1',
            'utf8': '1',
            'srnamespace': '0|4',
            'srinterwiki': '1',
        })
        resp_code = resp.status_code
        if resp_code != 200:
            time.sleep(3)
            continue
        resp_json = resp.json()
        # logging.info(str(resp_json))
        if len(resp_json['query']['search']) > 0:
            ids = list(map(lambda d: d['title'], filter( lambda x: x['title'][0]=='Q', resp_json['query']['search'])))
            return ids
    return []


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


# wikidata_query.get_qnumber_sparql(
#                wikisearch=author, birthdate_begin="1800", birthdate_end="1899")

ent_count=0

def select_entity(entities):
    global ent_count
    resp_code = 0
    join_entities = '|'.join(entities)
    while resp_code != 200:
        # time.sleep(1)
        logging.info(str(join_entities))
        resp = get('https://www.wikidata.org/w/api.php', {
            'action': 'wbgetentities',
            'ids': join_entities,
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
                    P569birthdate = get_year(P569birthdate)
                    print(P569birthdate)
                    if P569birthdate and ((int(P569birthdate) <= bstartdate) or (int(P569birthdate) > benddate)):
                        continue
                # print(str(P570deathdate))
                if P570deathdate:
                    P570deathdate = get_year(P570deathdate)
                    print(P570deathdate)
                    if P570deathdate and ((int(P570deathdate) <= dstartdate) or (int(P570deathdate) > denddate)):
                        continue
                if not(P569birthdate or P570deathdate):
                    continue
                return [wid, 'https://www.wikidata.org/wiki/'+wid]
    ent_count=ent_count+1
    id='random_id'+generate_string_id(ent_count)
    return [id, id]


def main():
    global ent_count

    parser = argparse.ArgumentParser(
        prog='Wikidata search', description='Search persons in wikidata')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                        help='csv file for processing', default=default_source_file)
    parser.add_argument('outfile', type=argparse.FileType('r', encoding='utf-8'), nargs='?',
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
        res_fieldnames = reader.fieldnames
        for line in reader:
            # ряд для ptable
            row = line
            to_search = ''
            dup=None
            dup=next((item for item in ptable if line["source"] == item["source"]), None)
            if dup:
                continue
            if line[sourcecols[0]]:
                to_search = line[sourcecols[0]]
            else:
                to_search = line[sourcecols[1]]
            mult=re.search(r'[ыи]м$',line[sourcecols[2]])
            if mult:
                to_search = f"{line[sourcecols[2]][:-2]}* {line[sourcecols[3]]}"
            stopword=re.search(r'[«»\?]', line[sourcecols[2]])
            unknown=re.search(r'еизвес', line[sourcecols[2]])
            notinitials=not re.search(r'[а-яa-z]', line[sourcecols[2]])
           
            row['wikidata_id'], row['wikidata_url'] = ['','']
            if (len(to_search)>2) and not (stopword or unknown or notinitials):
                search_res = get_qnumbers(to_search)
                if search_res:
                    row['wikidata_id'], row['wikidata_url'] = select_entity(search_res)

            if not row['wikidata_id']:
                ent_count=ent_count+1
                id='random_id'+generate_string_id(ent_count)
                row['wikidata_id'], row['wikidata_url'] = [id, id]

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
