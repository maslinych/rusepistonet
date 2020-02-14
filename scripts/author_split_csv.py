# Зависимости
# Python 3.8 https://www.python.org/downloads/
# Ms Excel
# pip install xlwings
# pip install pymorphy2
# pip install -U pymorphy2-dicts-ru
#
# Грязный хак без которого xlwings не заработал:
# в папке где установлен Python - скопировать dll-ки из Lib/site-packages/pywin32_system32 в Lib\site-packages\win32
# файлы примерно: pythoncom38.dll и pywintypes38.dll
#
# Установка панели xlwings в Excel - xlwings addin install
# Скрипт должен находиться в одной папке в документом excel и называться также, кроме расширения
# перечень.xslx перечень.py

import csv
import re
import logging
# Логирование в utf-8 для отладки 
logging.basicConfig(handlers=[logging.FileHandler(r"xlwings2.log", 'w', 'utf-8')], level=logging.INFO)



sourcecol='автор'
rescolnames=[r'авторФамилия',r'авторИмя',r'авторОтчество',r'авторPrim']

IOdot = re.compile(r'[А-Я]\.') # регулярное выражение для определения И. О.
EndComma = re.compile(r',$') # запятые в конце слов
EndDot = re.compile(r'[А-Я][а-я]+[.]$') #Фамилии с точкой на конце
FIO =  re.compile(r'[А-Я]\. [А-Я]\. [А-Я][а-я]+') #регулярное выражение для И. О. Фамилия
HardSur = ["Черкасск", "Неизвест", "Кохановс", "Грот"] # Слова и фамилии которые должны быть обработаны, но не детектируются другими подходами

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

def safe_list_get (l, idx, default):
  try:
    return l[idx]
  except IndexError:
    return default

       
def split_author(_line,_res_fieldnames):

    res_line=[dict()]
    for field in _res_fieldnames:
        res_line[0][field]=_line.get(field)
    cell=_line[sourcecol]  # получаем значение автора
    rownum=0

    if not cell: # пропускаем пустые ячейки
        return res_line

    #пробуем разделить ячейку по ; - вдруг несколько авторов
    authorz=cell.split(";")
    count_authorz=len(authorz)
    #logging.info(str(authorz))
    # запускаем цикл по авторам (даже если один), с номером текущего автора
    FioEnded=False
    for nauth,author in enumerate(authorz, start=0):
        if author=="":
            continue                
        #logging.info("nauth "+str(nauth))
        #logging.info("author "+str(nauth))

        #Разделяем ФИО автора на Ф И О
        lst=[]
        base_lst = author.split(",")
        lst.append(safe_list_get(base_lst,0,""))
        lst+=" ".join(base_lst[1:]).split()
        #logging.info("lst "+str(lst))

        # Запускаем цикл по ФИО автора с номером текущего слова

        for num,word in enumerate(lst, start=0):
            #logging.info("num "+str(num))
            #logging.info("word "+word)

            # Если и у нас только три слова - Ф И О - то записываем их в соответствующие столбцы
            # и отпиливаем запятые, если есть
            if re.findall("^[\(\[]",word):
                FioEnded=True

            if not FioEnded:
                 rescolnum=(3 if num > 3 else num )
                 res_line[rownum][rescolnames[rescolnum]]=word.replace(',','').strip()
            # Если слов больше 3 - дописываем в третий столбец, к отчеству
            else:
                try:
                    cellval=res_line[rownum][rescolnames[3]]
                    if not cellval:
                        cellval=""
                except IndexError:
                    cellval=""
                res_line[rownum][rescolnames[3]]=(cellval+' '+re.sub(r'[\)\(\[\])]','',word).strip()).strip()

            if re.findall("[\)\]]$",word):
                FioEnded=False       
        if FioEnded:
            count_authorz-=1

        # Больше одного автора - добавляем строку
        if count_authorz>1 and (rownum+1)<count_authorz and not FioEnded:
            rownum=rownum+1
            res_line+=[dict()]
            for field in _res_fieldnames:
                res_line[rownum][field]=""
        
    return res_line

def main():

    with open("../data/muratova.csv", newline='', encoding='utf-8-sig') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        res_fieldnames=reader.fieldnames+rescolnames
        with open("../data/muratova_res0.csv", "w", newline='', encoding='utf-8-sig') as resfile:
            writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';')
            writer.writeheader()
        for line in reader:
            cell=line[sourcecol]
            if not cell: # пропускаем пустые ячейки
                continue          
            res_lines=split_author(line,res_fieldnames)
            with open("../data/muratova_res0.csv", "a", newline='', encoding='utf-8-sig') as resfile:
                writer = csv.DictWriter(resfile, fieldnames=res_fieldnames, delimiter=';')
                for res_line in res_lines:
                    writer.writerow(res_line)



if __name__ == '__main__':
    main()
