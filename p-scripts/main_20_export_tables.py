#!/usr/bin/env python
# coding: utf-8
import logging
import sys
import csv
import argparse
import re

# формируем 3 таблицы - sources, individuals, letters


default_source_file = '../data/muratova_res14.csv'
default_persons_file = '../data/persons_table_res13.csv'
default_dest_sources = '../data/sources.csv'
default_dest_invidiuals = '../data/individuals.csv'
default_dest_letters = '../data/letters.csv'

# Логирование в utf-8 для отладки
logging.basicConfig(
    handlers=[logging.StreamHandler(sys.stdout)], level=logging.INFO)

# exclude_list=['неизвест','неустановл','родные','родным','аноним', 'вяземские']

def main():
    parser = argparse.ArgumentParser(prog='Fill nodes and edges', description='Fill nodes and edges')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                    help='csv file for processing', default=default_source_file)
    parser.add_argument('infile2',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                    help='csv file 2 for processing', default=default_persons_file)
    parser.add_argument('outfile_s',  type=argparse.FileType('w', encoding='utf-8'), nargs='?',
                    help='output file sources', default=default_dest_sources)
    parser.add_argument('outfile_i',  type=argparse.FileType('w', encoding='utf-8'), nargs='?',
                    help='output file individuals', default=default_dest_sources)
    parser.add_argument('outfile_l',  type=argparse.FileType('w', encoding='utf-8'), nargs='?',
                    help='output file letters', default=default_dest_sources)

    args = parser.parse_args()
    infile_data = args.infile.name
    infile2_data = args.infile2.name
    outfile_s = args.outfile_s.name
    outfile_i = args.outfile_i.name
    outfile_l = args.outfile_l.name

    ltable = []
    with open(infile_data, newline='', encoding='utf-8') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        for line in reader:
            ltable.append(line)

    ptable = []
    with open(infile2_data, newline='', encoding='utf-8') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        for line in reader:
            ptable.append(line)

    mapping = {}
    for line in ptable:
        mapping[line["wikidata_id"]] = line["fio_short"]

    sourcetable = []
    sourcecounter = 1
    individualtable = []
    individualcounter = 1
    letterstable = []
    letterscounter = 1

    for line in ltable:
        sourcerow={}
        source_id=0
        dup=False
        for source in sourcetable:
            if source['source_full'] == line['publication']:
                dup=True
                source_id=source['source_id']
                break
        if not dup:
            sourcerow['source_id']=sourcecounter
            source_id=sourcerow['source_id']
            sourcecounter+=1
            sourcerow['source_full']=line['publication']
            sourcerow['source_year']=line['publication_year']
            sourcerow['title']=''
            sourcerow['n_vol']=''
            sourcerow['place']=''
            sourcetable.append(sourcerow)

        individualrow={}
        dup=False
        for person in individualtable:
            if person['person_wikidata_id'] == line['auth_wikidataid']:
                dup=True
                from_id=person['person_id']
                break
        if not dup:
            individualrow['person_id']=individualcounter
            from_id=individualrow['person_id']
            individualcounter+=1
            individualrow['person_wikidata_id']=line['auth_wikidataid']
            personrow={}
            for item in ptable:
                if line['auth_wikidataid'] == item["wikidata_id"]:
                    if not personrow:
                        personrow=item
                    else:
                        for key in item:
                            if key in personrow and not personrow[key] and item[key]:
                                personrow[key]=item[key]
            individualrow['person_name']=personrow['fio_short']
            individualrow['person_full_name']=personrow['fio_full']
            individualrow['person_other_names']=line['author_note']
            individualrow['sex']=''
            individualrow['year_birth']=personrow['wikidata_birthdate']
            individualrow['year_death']=personrow['wikidata_enddate']
            individualrow['occupation']=line['author_occupation']
            individualrow['other']=''
            individualtable.append(individualrow)

        individualrow={}
        dup=False
        for person in individualtable:
            if person['person_wikidata_id'] == line['dest_wikidataid']:
                to_id=person['person_id']
                dup=True
                break
        if not dup:
            individualrow['person_id']=individualcounter
            to_id=individualrow['person_id']
            individualcounter+=1
            individualrow['person_wikidata_id']=line['dest_wikidataid']
            personrow={}
            for item in ptable:
                if line['dest_wikidataid'] == item["wikidata_id"]:
                    if not personrow:
                        personrow=item
                    else:
                        for key in item:
                            if key in personrow and not personrow[key] and item[key]:
                                personrow[key]=item[key]
            individualrow['person_name']=personrow['fio_short']
            individualrow['person_full_name']=personrow['fio_full']
            individualrow['person_other_names']=line['personalities_note']
            individualrow['sex']=''
            individualrow['year_birth']=personrow['wikidata_birthdate']
            individualrow['year_death']=personrow['wikidata_enddate']
            individualrow['occupation']=''
            individualrow['other']=''
            individualtable.append(individualrow)


        letterrow = {}
        letterrow['from']=from_id
        letterrow['to']=to_id
        letterrow['n_letters']=line['personalities_lett_count']
        letterrow['letter_year_start']=line['personalities_dates']
        letterrow['letter_year_end']=line['personalities_dates']
        letterrow['lettermonthstart']=''
        letterrow['lettermonthend']=''
        letterrow['source_id']=source_id
        letterrow['source_pages']=''
        letterrow['publication_year_start']=line['publication_year']
        letterrow['publication_year_end']=line['publication_year']
        letterrow['publication_type']=line['publication_type']
        letterstable.append(letterrow)



    # default_dest_letters
    # default_dest_invidiuals
    # default_dest_sources
    with open(default_dest_sources, 'w', encoding='utf-8', newline='') as outfile:
        fieldnames = list(sourcetable[0].keys())
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for item in sourcetable:
            writer.writerow(item)

    with open(default_dest_invidiuals, 'w', encoding='utf-8', newline='') as outfile:
        fieldnames = list(individualtable[0].keys())
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for item in individualtable:
            writer.writerow(item)

    with open(default_dest_letters, 'w', encoding='utf-8', newline='') as outfile:
        fieldnames = list(letterstable[0].keys())
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for item in letterstable:
            writer.writerow(item)


if __name__ == '__main__':
    main()
