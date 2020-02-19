# Зависимости
# Python 3.8 https://www.python.org/downloads/
# pip install pymorphy2
# pip install -U pymorphy2-dicts-ru

import pymorphy2
from pymorphy2.shapes import restore_capitalization
import re
import logging
import csv
import argparse

# Логирование в utf-8 для отладки 
logging.basicConfig(handlers=[logging.FileHandler(r"xlwings.log", 'w', 'utf-8')], level=logging.INFO)

# Запуск анализатора морф
morph = pymorphy2.MorphAnalyzer()

sourcecol = 'персоналии' # Столбец со строками для обработки
rescol = 'персонали_Ип' # столбец куда надо будет записать данные
rescol_prim = 'персоналии_примечание' # Столбец для примечаний (содержимое скобок)

IOdot = re.compile(r'^[А-ЯЁ]\.$') # регулярное выражение для определения И. О.
MultiIO = re.compile(r'^[А-ЯЁ]\. [А-ЯЁ]\.,$') # регулярное выражение для определения И. О.
EndSym = re.compile(r'[,;\)\]]$') # небуквенные символы в конце слов
BeginSym = re.compile(r'^[\[\(]') # небуквенные символы в начале слов
EndDot = re.compile(r'[А-ЯЁ][а-яё]+\.$') #Фамилии с точкой на конце
FIO_iof =  re.compile(r'^([А-ЯЁ]\. )?[А-ЯЁ]\. [А-ЯЁ][а-яё]+$') #регулярное выражение для И. О. Фамилия
FIO_fio =  re.compile(r'^[А-ЯЁ][а-яё]+ [А-ЯЁ]\.( [А-ЯЁ]\.)?$') #регулярное выражение для Фамилия И.О.
HardSur = ["Черкасск", "Неизвест", "Кохановс", "Грот", "Огарёв"] # Слова и фамилии которые должны быть обработаны, но не детектируются другими подходами

# Потенциальные теги для определения фамилий
keys_poss_fio= ['Surn','Geox','Orgn','Trad','anim']
# Фамилия, топоним, организация, торговая марка, Одушевленное
# http://opencorpora.org/dict.php?act=gram
# Проверяется наличие хотя бы одного тега в каждом варианте разбора

# Поиск наличия хотя бы одного из тегов в списке тегов слова
def test_tag_list(_keys, _tags):
    for key in _keys:
        if key in _tags:
            return True
    return False

# Поиск на соответствие списку трудных для детекции слов
def test_match_hard(_word):
    for one in HardSur:
        result=re.match(one, _word)
        if result:
            return True

def safe_list_get (l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default

def extract_person(_celldata):
    res_cell=re.search(r'^(.*)\([0-9?]+\)',_celldata, re.IGNORECASE)
    if res_cell:
        res_cell=res_cell.group(1)
    else:
        return ""
    res_cell=res_cell.strip()
    if res_cell.endswith('.'):
        res_cell=res_cell[:-1]
    res_cell=re.sub(r"\s\s+", " ", res_cell)
    return res_cell

def convert_to_ip(_person):
    lst = _person.split() # разделяем ячейку на отдельные слова
    words = []
    for cur_word in lst:
        word=cur_word
# EndSym = re.compile(r'[,;\)\]]$') # небуквенные символы в конце слов
# BeginSym = re.compile(r'^[\[\(]') # небуквенные символы в начале слов
        # Проверяем на дополнительный символ в конце слова (скобка,запятая,точка запятой). Если найден - отпиливаем. И запоминаем, чтобы вернуть в конце
        HasEndSym=False
        if re.findall(r'[,;\)\]»\"\']$',word):
            HasEndSym=True
            EndSymSave=word[-1]
            word=word[:-1]

        # Отпиливаем точку и запоминаем
        HasEndDot=False
        if word.endswith('.'):
            HasEndDot=True
            word=word[:-1]

        #Проверяем, запоминаем если есть и отпиливаем небуквенный символ в начале слова
        HasBeginSym=False
        if re.findall(r'^[«\'\"\[\(]',word):
            HasBeginSym=True
            BeginSymSave=word[0]
            word=word[1:]
        
        # Пропускаем слова из одной буквы (инициалы, союзы и проч)
        # Добавляем их в результирующий массив без изменений
        if len(word)==1:
            words.append(cur_word)
            continue

        parsed = morph.parse(word)  # вызываем разбор слова в pymorphy
        p=None
        
        for variant in parsed:
            # Смотрим варианты разбора, определяем более подходящий
            # тот, у которого будет хотя бы один из заданных тегов
            # и дательный падеж
            if test_tag_list(['datv'],variant.tag) and test_tag_list(keys_poss_fio, variant.tag):
                p=variant
                break

        # Если такого не найдено - берем первый вариант.
        if not p:
            p=parsed[0]
        if p.inflect({'nomn'}):
            res=p.inflect({'nomn'}).word # приводим слово в И.П. (число не меняем)

            res=restore_capitalization(res,word) #Возвращаем заглавные буквы где они были

            if HasEndDot:
                res=res+'.'
            if HasEndSym: # если был символ в конце - возвращаем
                res=res+EndSymSave
            if HasBeginSym: # если был символ в начале - возвращаем
                res=BeginSymSave+res

            words.append(res) # добавляем в результирующий список
            logging.info('final word status: '+res)
        else:
            words.append(word)


    return ' '.join(words) 

def main():

    parser = argparse.ArgumentParser(prog='Personalii convert', description='Extract personalies into another column and/or modify them')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8-sig'), nargs='?',
                    help='csv file for processing', default="../data/muratova.csv")
    parser.add_argument('outfile', type=argparse.FileType('w', encoding='utf-8-sig'), nargs='?',
                    help='csv file for output', default="../data/muratova_res.csv")
    args = parser.parse_args()
    infile=args.infile.name
    outfile=args.outfile.name

    with open(infile, newline='', encoding='utf-8-sig') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        res_fieldnames=reader.fieldnames+[rescol]
        with open(outfile, "w", newline='', encoding='utf-8-sig') as resfile:
            writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';')
            writer.writeheader()
        for line in reader:
            cell=line[sourcecol]
            if not cell: # пропускаем пустые ячейки
                continue          
            extracted_person=extract_person(cell)
            if not extracted_person:
                continue
            person_ip=convert_to_ip(extracted_person)
            res_line=line
            res_line[rescol]=person_ip
            with open(outfile, "a", newline='', encoding='utf-8-sig') as resfile:
                writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';')
                writer.writerow(res_line)


if __name__ == '__main__':
    main()