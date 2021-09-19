# Зависимости
# Python 3.8 https://www.python.org/downloads/
# pip install pymorphy2
# pip install -U pymorphy2-dicts-ru русский словарь

# колонка "персоналии" (адресаты) - преобразуем фаимилии адресатов в единственное число, именительный падеж
# с помощью пакета pymorphy2, русского словаря для него и приготовленных вручную исключений

import pymorphy2
# возвращает заглавные буквы после преобразования
from pymorphy2.shapes import restore_capitalization
import re
import csv
import argparse
from import_exclusions import exclusions_phrase, exclusions_word


# Запуск анализатора морф
morph = pymorphy2.MorphAnalyzer()

default_source_file = '../data/muratova_res09.csv'
default_dest_file = '../data/muratova_res10.csv'
sourcecol = 'фамилия_неделимо'  # столбец со строками для обработки
rescols = ['адресатИП']  # столбцы, куда надо будет записать данные

# Поиск наличия хотя бы одного из тегов в списке тегов слова


def test_tag_list(_keys, _tags):
    for key in _keys:
        if key in _tags:
            return True
    return False


def convert_to_ip(_person):
    lst = _person.split()  # разделяем ячейку на отдельные слова
    InQuotes = False
    words = []
    # Если фраза есть в списке исключений
    if exclusions_phrase.get(_person):
        phrase = exclusions_phrase.get(_person)  # Забираем готовую форму ИП
        return {rescols[0]: phrase}

    for cur_word in lst:
        ShouldSkip = False
        word = cur_word

        if cur_word.startswith('«'):
            InQuotes = True

        if InQuotes:
            ShouldSkip = True

        if cur_word.endswith('»'):
            InQuotes = False

        # Если слово заканчивается на точку - пропускаем, сокращение
        if word.endswith('.') or ShouldSkip:
            words.append(cur_word)
            continue

        # Проверяем на дополнительный символ в конце слова (скобка,запятая,точка запятой). Если найден - отпиливаем. И запоминаем, чтобы вернуть в конце
        HasEndSym = False
        if re.findall(r'[,;\)\]»\"\']$', word):
            HasEndSym = True
            EndSymSave = word[-1]
            word = word[:-1]

        # Проверяем, запоминаем если есть и отпиливаем небуквенный символ в начале слова
        HasBeginSym = False
        if re.findall(r'^[«\'\"\[\(]', word):
            HasBeginSym = True
            BeginSymSave = word[0]
            word = word[1:]

        # Если слово есть в списке исключений
        if exclusions_word.get(word):
            word = exclusions_word.get(word)  # Забираем готовую форму ИП
            if HasEndSym:  # если был символ в конце - возвращаем
                word = word+EndSymSave
            if HasBeginSym:  # если был символ в начале - возвращаем
                word = BeginSymSave+word
            words.append(word)  # добавляем в результирующий список
            continue

        # Пропускаем слова из одной буквы (инициалы, союзы и проч)
        # Добавляем их в результирующий массив без изменений
        if len(word) == 1:
            words.append(cur_word)
            continue

        parsed = morph.parse(word)  # вызываем разбор слова в pymorphy
        p = None

        for variant in parsed:
            # Смотрим варианты разбора, определяем более подходящий
            # тот, у которого будет хотя бы один из заданных тегов
            # и дательный падеж
            # and test_tag_list(keys_poss_fio, variant.tag):
            if test_tag_list(['datv'], variant.tag):
                p = variant
                break

        if p and p.inflect({'nomn'}):
            # приводим слово в И.П. (число не меняем)
            res = p.inflect({'nomn'}).word

            # Возвращаем заглавные буквы где они были
            res = restore_capitalization(res, word)

            if HasEndSym:  # если был символ в конце - возвращаем
                res = res+EndSymSave
            if HasBeginSym:  # если был символ в начале - возвращаем
                res = BeginSymSave+res

            words.append(res)  # добавляем в результирующий список
        else:
            words.append(cur_word)

    return {rescols[0]: ' '.join(words)}


def main():

    parser = argparse.ArgumentParser(
        prog='Personalii convert', description='Extract personalies into another column and/or modify them')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                        help='csv file for processing', default=default_source_file)
    parser.add_argument('outfile', type=argparse.FileType('w', encoding='utf-8'), nargs='?',
                        help='csv file for output', default=default_dest_file)
    args = parser.parse_args()
    infile = args.infile.name
    outfile = args.outfile.name

    with open(infile, newline='', encoding='utf-8') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        res_fieldnames = reader.fieldnames+rescols
        with open(outfile, "w", newline='', encoding='utf-8') as resfile:
            writer = csv.DictWriter(
                resfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
        for line in reader:
            cell = line[sourcecol]
            if cell:
                extracted_data = convert_to_ip(cell)
            else:
                extracted_data = {rescols[0]: ""}

            line.update(extracted_data)
            with open(outfile, "a", newline='', encoding='utf-8') as resfile:
                writer = csv.DictWriter(
                    resfile, fieldnames=res_fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                writer.writerow(line)


if __name__ == '__main__':
    main()
