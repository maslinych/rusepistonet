import csv
import argparse
import glob
import os



def main():
    ptable = []
    for csv_file in glob.glob("*.csv"):
        print(csv_file)
        with open(csv_file, newline='', encoding='utf-8', newline='') as datafile:
            reader = csv.DictReader(datafile, delimiter=';')
            for line in reader:
                line["filename"]=csv_file
                # добавляем в список
                ptable.append(line)
    publications_list=[]
    for line in ptable:
        publ=line.get("публикация")
        if publ==None:
            print("Нет колонки публикация")
            print(line)
        else:
           if publ not in publications_list:
            publications_list.append(publ)
    print(publications_list)
    with open("publications_list.txt", "w", encoding='utf-8', newline='') as resfile:
        resfile.write("\n".join(publications_list))
if __name__ == '__main__':
    main()