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
EndSym = re.compile(r'[,;]$') # запятые в конце слов
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

def morph_to_ip(_cell):
    lst = _cell.split() # разделяем ячейку на отдельные слова
    indxlst = []
    words = []
    for num,cur_word in enumerate(lst, start=0):
    # Цикл по словам с индексом, для последующего выдергивания интересующих слов
    # Здесь только определяем номера слов, которые хотим выдернуть
        logging.info(cur_word)

        # Проверяем на запятую в конце слова. Если найдена - отпиливаем. 
        if EndSym.findall(cur_word):
            logging.info('end symbol found')
            word=cur_word[:-1]
        else:
            word=cur_word

        # Отпиливаем точку в конце слова, если она есть
        if EndDot.findall(word):
            word=word[:-1]

        logging.info(word)

        parsed = morph.parse(word) # вызываем разбор слова в pymorphy

        p=None
        for variant in parsed: # Смотрим варианты разбора, определяем более подходящий
            # тот, у которого будет хотя бы один из заданных тегов
            if test_tag_list(keys_poss_fio, variant.tag):
                p=variant
                break
        # Если такого не найдено - берем первый вариант.
        if not p:
            p=parsed[0]

        logging.info(p.tag)

        # Если слово - это скорее всего фамилия или из списка сложных слов
        if test_tag_list(keys_poss_fio, p.tag) or test_match_hard(word):
            logging.info('test_tag_list succ')
            # Вяло защищаемся от месяцев (Март, Май) - их детектирует pymorphy
            if num > 0 and lst[num-1].isnumeric():
                continue

            # Поскольку это потенциально фамилия - значит надо прихватить два слова перед данным.
            if num > 1:
                indxlst.append(num-2)
            if num > 0:
                indxlst.append(num-1)
            indxlst.append(num)


        if (num > 1):
            last_3=" ".join([lst[num-2],lst[num-1],lst[num]])
        if (num > 0):
            last_2=" ".join([lst[num-1],lst[num]])

        if (num > 1) and FIO_iof.match(last_3):
            indxlst.append(num-2)
            indxlst.append(num-1) 
            indxlst.append(num)

        if (num > 0) and FIO_fio.match(last_2):
            indxlst.append(num-1) 
            indxlst.append(num)

        if (num > 0) and (MultiIO.match(last_2)):
            indxlst.append(num-1) 
            indxlst.append(num)

        # if (IOdot.match(lst[num])):
        #     indxlst.append(num)
        
        logging.info (indxlst)
    
    indxlst = sorted(set(indxlst)) # Сортируем по возрастанию, убираем повторяющиеся номера
    logging.info (indxlst)

    # Начинаем выдергивать слова по номерам, приводить их в именительный падеж единственное число
    for num in indxlst:
        word=lst[num] #Получаем слово
        
        # Проверяем на запятую в конце слова. Если найдена - отпиливаем. И запоминаем, чтобы вернуть в конце
        HasEndSym=False
        if EndSym.findall(word):
            HasEndSym=True
            EndSymSave=word[-1]
            word=word[:-1]

        # Отпиливаем точку
        HasEndDot=False
        if word.endswith('.'):
            HasEndDot=True
            word=word[:-1]

        logging.info(word)

        if len(word)>1:
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

            logging.info(p.tag)
            #if test_tag_list(keys_poss_fio, p.tag) or test_match_hard(word):

            # Смотрим что это слово или сложное для детектирования слово
            #if p.inflect({'sing','nomn'}):
            #    res=p.inflect({'sing','nomn'}).word # приводим слово в И.П. единственное число
            if p.inflect({'nomn'}):
                res=p.inflect({'nomn'}).word # приводим слово в И.П. (число не меняем)
                #    res=""
                #if  test_tag_list(keys_poss_fio, p.tag) or test_match_hard(word):
                res=res.title()

                if HasEndSym: # если была запятая - возвращаем
                    res=res+EndSymSave

                words.append(res) # добавляем в результирующий список
                logging.info('final word status: '+res)
            else:
                words.append(word)
        else:
        # Не фамилия - оставляем без обработки
            words.append(lst[num])

    return ' '.join(words) #Возвращаем в качестве результата найденные слова в И.П. единственное число

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

        # Проверяем на запятую в конце слова. Если найдена - отпиливаем. И запоминаем, чтобы вернуть в конце
        HasEndSym=False
        if EndSym.findall(word):
            HasEndSym=True
            EndSymSave=word[-1]
            word=word[:-1]

        # Отпиливаем точку и запоминаем
        HasEndDot=False
        if word.endswith('.'):
            HasEndDot=True
            word=word[:-1]
        
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
            if HasEndSym: # если была запятая - возвращаем
                res=res+EndSymSave

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