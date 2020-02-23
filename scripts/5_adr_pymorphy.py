# Зависимости
# Python 3.8 https://www.python.org/downloads/
# pip install pymorphy2
# pip install -U pymorphy2-dicts-ru русский словарь

import pymorphy2
from pymorphy2.shapes import restore_capitalization #возвращает заглавные буквы после преобразования
import re
import csv
import argparse


# Запуск анализатора морф
morph = pymorphy2.MorphAnalyzer()

sourcecol = 'адресат_одиночн' # столбец со строками для обработки
rescols = ['адресатИ', 'адресатО', 'адресатФ'] # столбцы, куда надо будет записать данные

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

def extract_data_person3(_celldata):
    res_cell=re.search(r'^([А-ЯЁ][а-яё\-]*\.) ([А-ЯЁ][а-яё\-]*\.)? ?([А-ЯЁа-яё-]+)$',_celldata, re.IGNORECASE) 
    if res_cell:
        Im=res_cell.group(1)
        Otch=res_cell.group(2)
        Fam=convert_to_ip(res_cell.group(3))
        return [Im,Otch,Fam]
    else:
        data=convert_to_ip(_celldata)
        return ["","",data]

    return ["","",""]

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
        else:
            words.append(word)


    return ' '.join(words) 

def main():

    parser = argparse.ArgumentParser(prog='Personalii convert', description='Extract personalies into another column and/or modify them')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8-sig'), nargs='?',
                    help='csv file for processing', default="../data/muratova_res4.csv")
    parser.add_argument('outfile', type=argparse.FileType('w', encoding='utf-8-sig'), nargs='?',
                    help='csv file for output', default="../data/muratova_res5.csv")
    args = parser.parse_args()
    infile=args.infile.name
    outfile=args.outfile.name

    with open(infile, newline='', encoding='utf-8-sig') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        res_fieldnames=reader.fieldnames+rescols
        with open(outfile, "w", newline='', encoding='utf-8-sig') as resfile:
            writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';')
            writer.writeheader()
        for line in reader:
            cell=line[sourcecol]
            if cell: 
                extracted_data=extract_data_person3(cell)
            else:
                extracted_data=["","",""]
            res_line=line
            for num,col in enumerate(rescols, start=0):
                res_line[col]=extracted_data[num]
            with open(outfile, "a", newline='', encoding='utf-8-sig') as resfile:
                writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';')
                writer.writerow(res_line)


if __name__ == '__main__':
    main()