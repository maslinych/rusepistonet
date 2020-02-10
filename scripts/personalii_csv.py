# Зависимости
# Python 3.8 https://www.python.org/downloads/
# pip install pymorphy2
# pip install -U pymorphy2-dicts-ru

import pymorphy2
import re
import logging
import csv

# Логирование в utf-8 для отладки 
logging.basicConfig(handlers=[logging.FileHandler(r"xlwings.log", 'w', 'utf-8')], level=logging.INFO)

# Запуск анализатора морф
morph = pymorphy2.MorphAnalyzer()

sourcecol = 'персоналии' # Столбец со строками для обработки
rescol = 'персонали_Ип' # столбец куда надо будет записать данные

IOdot = re.compile(r'[А-Я]\.') # регулярное выражение для определения И. О.
EndComma = re.compile(r',$') # запятые в конце слов
EndDot = re.compile(r'[А-Я][а-я]+[.]$') #Фамилии с точкой на конце
FIO =  re.compile(r'[А-Я]\. [А-Я]\. [А-Я][а-я]+') #регулярное выражение для И. О. Фамилия
HardSur = ["Черкасск", "Неизвест", "Кохановс", "Грот"] # Слова и фамилии которые должны быть обработаны, но не детектируются другими подходами

# Потенциальные теги для определения фамилий
keys_poss_fio= ['anim','Surn','Geox','Orgn','Trad']
# Одушевленное, Фамилия, топоним, организация, торговая марка
# http://opencorpora.org/dict.php?act=gram
# Проверяется наличие хотя бы одного тега в каждом варианте разбора

# Поиск наличия хотя бы одного из тегов в списке тегов слова
def test_tag_list(keys, tags):
    for key in keys:
        if key in tags:
            return True
    return False

# Поиск на соответствие списку трудных для детекции слов
def test_match_hard(_word):
    for one in HardSur:
        result=re.match(one, _word)
        if result:
            return True

def main():

    with open("../data/muratova.csv") as datafile:
        reader = csv.DictReader(datafile, delimiter=',')
        for line in reader:
            print(line["first_name"]),
            print(line["last_name"])

    if xw.Range(sourcecol+str(1)).value != r'персоналии':
        raise AssertionError(r'Проверьте переменную sourcecol - заголовок столбца '+sourcecol+'не "персоналии"')

    if xw.Range(rescol+str(1)).value != r'персоналииИП':
        xw.Range(rescol+":"+rescol).api.Insert(InsertShiftDirection.xlShiftToRight)
        xw.Range(rescol+str(1)).value=r'персоналииИП'

    for rownum in range(sourcerowstart,sourcerowend):
    # цикл от sourcerowstart до sourcerowend
        cell=xw.Range(sourcecol+str(rownum)).value # получаем значение ячейки
        rescell=xw.Range(rescol+str(rownum)) # получаем целевую ячейку для записи в конце итерации
        if not cell: # пропускаем пустые ячейки
            continue
        lst = cell.split() # разделяем строку на отдельные слова
        indxlst = []
        words = []
        for num,_word in enumerate(lst, start=0):
        # Цикл по словам с индексом, для последующего выдергивания интересующих слов
        # Здесь только определяем номера слов, которые хотим выдернуть
            logging.info(_word)

            # Проверяем на запятую в конце слова. Если найдена - отпиливаем. 
            if EndComma.findall(_word):
                logging.info('comma found')
                word=_word[:-1]
            else:
                word=_word

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
            elif (num > 1) and FIO.match(lst[num-2]+lst[num-1]+lst[num]):
            # Pymorphy не определил фамилию, но подпадает под regex
                indxlst.append(num)
            elif 'CONJ' in  p.tag:
            # Слово является союзом - "И" тоже вытаскиваем для удобства чтения
                indxlst.append(num)
            #elif IOdot.match(word):
            # Не пригодилось в силу первого варианта - отдельно вытаскивать И. О.
            # слишком много ложных срабатываний
            #    logging.info('iodot found')
            #    indxlst.append(num)
            logging.info (indxlst)
        
        indxlst = sorted(set(indxlst)) # Сортируем по возрастанию, убираем повторяющиеся номера
        logging.info (indxlst)

        # Начинаем выдергивать слова по номерам, приводить их в именительный падеж единственное число
        for num in indxlst:
            _word=lst[num] #Получаем слово

            # Проверяем на запятую в конце слова. Если найдена - отпиливаем. И запоминаем, чтобы вернуть в конце
            if EndComma.findall(_word):
                HasEndComma=True
                word=_word[:-1]
            else:
                HasEndComma=False
                word=_word

            # Отпиливаем точку
            if EndDot.findall(word):
                word=word[:-1]

            logging.info(word)
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
            if test_tag_list(keys_poss_fio, p.tag) or test_match_hard(word) and not test_tag_list(['CONJ'],p.tag):
            # Смотрим что это слово или сложное для детектирования слово, и не союз (хотя не помогает такая проверка, потому что теги значимей)
                if p.inflect({'sing','nomn'}):
                    res=p.inflect({'sing','nomn'}).word # приводим слово в И.П. единственное число
                else:
                    res=""
                if res != r'и': # если не союз И - делаем первые буквы заглавными
                    res=res.title()

                if HasEndComma: # если была запятая - возвращаем
                    res=res+','

                words.append(res) # добавляем в результирующий список
                logging.info('final word status: '+res)
            else:
            # Не фамилия - оставляем без обработки. Только запятую возвращаем если была
                if HasEndComma:
                    words.append(word+',')
                else:
                    words.append(word)

        rescell.value=' '.join(words) #Записываем в ячейку результата найденные слова в И.П. единственное число
        #rescellQ.value=get_qnumber(wikisearch=author.replace(',','').strip(), wikisite="wikidatawiki")


if __name__ == '__main__':
    main()