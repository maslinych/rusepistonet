# Зависимости
# Python 3.8 https://www.python.org/downloads/
# qwikidata

# сохраняем в отдельный файл персоналии - авторы и адресаты

import pymorphy2
# возвращает заглавные буквы после преобразования
from pymorphy2.shapes import restore_capitalization
import re
import logging
import time
import sys
import csv
import argparse
from import_exclusions import exclusions_phrase, exclusions_word

from requests import get
import wikidata_query

# Логирование в utf-8 для отладки
logging.basicConfig(
    handlers=[logging.StreamHandler(sys.stdout)], level=logging.INFO)

default_source_file = '../data/muratova_res10.csv'
default_dest_file = '../data/persons_table_res11.csv"'
# столбцы со строками для обработки
sourcecols = ['автор', 'адресат_ио', 'адресатИП', 'фамилия_неделимо']
#rescols = ['authorwikidataurl', 'authorwikidataid', 'adrwikidataurl',
           #'adrwikidataid']  # столбцы, куда надо будет записать данные

rescols = ['source', 'fam', 'io', 'io_short', 'fam_single', 'fam_orig', 'fio_full', 'fio_short', 'wikidata_id','wikidata_url']

# Запуск анализатора морф
morph = pymorphy2.MorphAnalyzer()

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

#get_qnumber(wikisearch="Шелгунов Николай Васильевич", wikisite="wikidatawiki")
def get_qnumber(wikisearch, wikisite):

    author = wikisearch.split()
    if len(author) == 1:
        return ""
    variants = []
    variants.append(" ".join(author))
    if len(author) > 2:
        if author[2].endswith('.'):
            return ""
        if author[0] == r"Маркс":
            variants.append(" ".join([author[1], author[0]]))
            variants.append(" ".join([author[0], author[1]]))
        variants.append(" ".join([author[0], author[1], author[2]]))
        variants.append(" ".join([author[0]+",", author[1], author[2]]))
        variants.append(" ".join([author[0], author[2], author[1]]))
        variants.append(" ".join([author[1], author[2], author[0]]))
    # if len(author)>1:
    #     if author[1].endswith('.'):
    #         return ""
    #     variants.append(" ".join([author[0],author[1]]))
    #     variants.append(" ".join([author[1],author[0]]))

    for var in variants:
        # time.sleep(1)
        logging.info(str(var))
        resp = get('https://www.wikidata.org/w/api.php', {
            'action': 'wbsearchentities',
            'search': var,
            'props': '',
            'language': 'ru',
            'format': 'json',
            'formatversion': '2'
        }).json()
        logging.info(str(resp))
        if len(resp['search']) > 0:
            return resp['search'][0]['id']
    return ""


# wikidata_query.get_qnumber_sparql(
#                wikisearch=author, birthdate_begin="1800", birthdate_end="1899")

def ask_wikidata(cell):
    result = {}
    return result


# Получить фамилию в единственном числе
def convert_to_sing(_person):
    lst = _person.split()  # разделяем ячейку на отдельные слова

    #не пытаемся ничего делать и возвращаем как есть, если

    #больше одного слова
    if len(lst) > 1:
        return _person

    cur_word = _person

    # есть спецсимволы в слове
    if re.findall(r'^[«\'\"\[\(\.,;\)\]»\"\']', cur_word):
        return _person

    # если слово не заканчивается на "ы" (спорно, но без ложноположительных)
    if not cur_word.endswith(r'ы'):
        return _person

    # если слово всего из одного символа
    if len(cur_word) == 1:
        return _person

    parsed = morph.parse(cur_word)  # вызываем разбор слова в pymorphy
    p = None

    for variant in parsed:
        # Смотрим варианты разбора, определяем более подходящий
        # тот, у которого будет хотя бы один из заданных тегов
        # и множественное число
        if test_tag_list(['plur'], variant.tag):
            p = variant
            break

    if p and p.inflect({'sing', 'nomn'}):
        # приводим слово в И.П., единственное число
        res = p.inflect({'sing', 'nomn'}).word

        # Возвращаем заглавные буквы где они были
        res = restore_capitalization(res, cur_word)

        return res
    else:
        return cur_word

    return cur_word


def main():

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
    with open(outfile, newline='', encoding='utf-8') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        for line in reader:
            # добавляем в список
            ptable.append(line)

    with open(infile, newline='', encoding='utf-8') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        for line in reader:
            #ряд для ptable
            row = {}
            # смотрим автора письма
            author = line[sourcecols[0]]
            dup=None
            dup=next((item for item in ptable if author == item["source"]), None)
            if not dup and not ';' in author:
                # если есть спецсимволы - то не пытаемся выделить имя-отчество
                if re.findall(r'^[«\'\"\[\(\.,;\)\]»\"\']$', author):
                    ioshort=''
                    asplit=''
                else:
                    # в противном случае выделям имя-отчество для занесения
                    asplit = author.split(',')
                    # если одно слово - то И.О. точно нет
                    if len(asplit)==1:
                        ioshort = ''
                    else:
                        # получаем всё что после запятой, чистим от пробелов, делим на слова
                        iosplit = safe_list_get(asplit, 1, '').strip().split()
                        # выделяем имя
                        im = safe_list_get(safe_list_get(iosplit, 0, '').strip(),0,'')
                        # отпиливаем точку от имени, если есть - потом добавим к сокращению
                        if im and im[-1]=='.':
                            im=im[:-1]
                        # выделяем отчество, аналогично имени
                        otch = safe_list_get(safe_list_get(iosplit, 1, '').strip(),0,'')
                        if otch and otch[-1]=='.':
                            otch=im[:-1]
                        # если есть только имя - запоминаем его как инициалы И. о.
                        if len(iosplit)==1:
                            ioshort = im+'.'
                        # если есть имя и отчество - то записываем их как инициалы
                        elif len(iosplit)>1:
                            ioshort = im+'. '+otch+'.'
                        # если непонятно что - то записываем всё что не является фамилией
                        else:
                            ioshort = safe_list_get(asplit, 1, '').strip()
                # заполняем строку
                # автор в варианте "как есть"
                row['source'] = author
                # фамилия
                row['fam'] = safe_list_get(asplit, 0, '').strip()
                # имя отчество "как есть"
                row['io'] = safe_list_get(asplit, 1, '').strip()
                # и только инициалы
                row['io_short'] = ioshort
                # тут считаем что автор всегда записан полным именем - записываем
                row['fio_full'] = author
                # записываем Фамилия, И. О. для дальнейшего поиска
                row['fio_short'] = row['fam']+', '+ioshort
                # Фамилия в единственном числе - тут совпадает просто с фамилией
                row['fam_single'] = row['fam']
                row['fam_orig'] = row['fam']
                # Под данные с викидата
                row['wikidata_id'] = ''
                row['wikidata_url'] = ''
                # добавляем в список
                ptable.append(row)

            # обнуляем ряд
            row = {}
            # заполняем ряд для адресатов
            # Получаем фамилию и инициалы и склеиваем в строку по принципу как fio_short
            dest_fam = line[sourcecols[2]].strip()
            dest = dest_fam
            dest_io = ''
            if line[sourcecols[1]]:
                dest_io = line[sourcecols[1]].strip()
                dest = dest + ', ' + dest_io
            dup=None
            dup=next((item for item in ptable if dest == item["source"]), None)
            if not dup and not ';' in author:
                # адресат в формате "как есть" для поиска
                row['source'] = dest
                # только фамилия "как есть"
                row['fam'] = dest_fam
                row['fam_orig'] = line[sourcecols[3]]
                # только инициалы
                row['io'] = dest_io
                row['io_short'] = dest_io
                # фамилия в единственном числе, прогоняем через pymorphy
                row['fam_single'] = convert_to_sing(row['fam'])\
                # Полное имя неизвестно на данном этапе - у адресатов только инициалы
                row['fio_full'] = ''
                # зато Фамилия, И. О. у нас уже есть
                row['fio_short'] = (row['fam_single'] + ', ' + dest_io) if dest_io else row['fam_single']
                row['wikidata_id'] = ''
                row['wikidata_url'] = ''
                ptable.append(row)

    # колдунство, которое по стобцу source удаляет все повторяющиеся строки
    #ptable=list({item["source"]: item for item in ptable}.values())
    # сортируем список по столбцу source
    #ptable=sorted(ptable, key = lambda i: i['source'])

    # Предполагаем, что некоторые авторы также побывали и адресатами
    # По всему списку ищем тех, у кого Фамилия, И.О. совпадает с чьим-то сырым "source" именем, и при этом известно полное имя
    for p in ptable:
        d=next((item for item in ptable if (
            ((p["fio_short"] == item["source"]) or ((p["fam_single"] in item["fam_single"]) and (p["io_short"] == item["io_short"])) and
            p["io_short"] and item["io_short"]
            ) and 
            p["fio_full"] and 
            not item["fio_full"]
            )
            ), None)
        # заполняем найденное полное имя
        if d:
            logging.info(d)
            logging.info(p)
            d["io"]=p["io"]
            d["fio_full"]=p["fio_full"]
            d["fam_single"]=p["fam_single"]
            d["fio_short"]=p["fio_short"]

    #ptable=list({item["fio_short"]: item for item in ptable}.values())
    #ptable=sorted(ptable, key = lambda i: i['source'])

    with open(outfile, "w", newline='', encoding='utf-8') as resfile:
        writer = csv.DictWriter(resfile, fieldnames=rescols, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
    for line in ptable:
        with open(outfile, "a", newline='', encoding='utf-8') as resfile:
            writer = csv.DictWriter(resfile, fieldnames=rescols, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(line)


if __name__ == '__main__':
    main()

