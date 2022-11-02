#!/usr/bin/env python
# coding: utf-8
import logging
import sys
import csv
import argparse
import re
from pajek_tools import PajekWriter
import pandas as pd

# сохраняем в отдельный файлы сформированные грани и ноды для графа

default_source_file = '../data/muratova_res14.csv'
default_persons_file = '../data/persons_table_res13.csv'
default_pajek_net_file = '../data/muratova.net'
default_pajek_clu_file = '../data/muratova.clu'

map_ideol = {
    'слав' : '1',
    'запад': '2',
    ''     : '3'
}

# Логирование в utf-8 для отладки
logging.basicConfig(
    handlers=[logging.StreamHandler(sys.stdout)], level=logging.INFO)

exclude_list=['неизвест','неустановл','родные','родным','аноним', 'вяземские']

def main():
    parser = argparse.ArgumentParser(prog='Fill nodes and edges', description='Fill nodes and edges')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                    help='csv file for processing', default=default_source_file)
    parser.add_argument('infile2',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                    help='csv file 2 for processing', default=default_persons_file)
    parser.add_argument('outfile_net',  type=argparse.FileType('w', encoding='utf-8'), nargs='?',
                    help='output net file', default=default_pajek_net_file)
    parser.add_argument('outfile_clu',  type=argparse.FileType('w', encoding='utf-8'), nargs='?',
                    help='output clu file', default=default_pajek_clu_file)
    args = parser.parse_args()
    infile_data = args.infile.name
    infile2_data = args.infile2.name
    outfile_net = args.outfile_net.name
    outfile_clu = args.outfile_clu.name

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
    map_pers_ideol = {}
    for line in ptable:
        mapping[line["wikidata_id"]] = line["fio_short"]
        map_pers_ideol[line["wikidata_id"]] = map_ideol[line["ideology"]]

    edgetable = {}
    for line in ltable:
        if not line['auth_wikidataid'] or not line['dest_wikidataid']:
            continue
        if  any(re.search(x,line["personalities_nominative"],re.IGNORECASE) for x in exclude_list):
            continue
        edge = line['auth_wikidataid']+line['dest_wikidataid']
        rev_edge = line['dest_wikidataid']+line['auth_wikidataid']
        if edge not in edgetable.keys() and rev_edge not in edgetable.keys():
            edgetable[edge] = {}
            edgetable[edge]['auth_wikidataid'] = line['auth_wikidataid']
            edgetable[edge]['auth_fio_short'] = mapping[line['auth_wikidataid']]
            edgetable[edge]['dest_wikidataid'] = line['dest_wikidataid']
            edgetable[edge]['dest_fio_short'] = mapping[line['dest_wikidataid']]
            edgetable[edge]['auth_ideol'] = map_pers_ideol[line['auth_wikidataid']]
            edgetable[edge]['dest_ideol'] = map_pers_ideol[line['dest_wikidataid']]
            edgetable[edge]['weight']=1
        elif edge in edgetable.keys():
                edgetable[edge]['weight']=edgetable[edge]['weight']+1
        elif rev_edge in edgetable.keys():
                edgetable[rev_edge]['weight']=edgetable[rev_edge]['weight']+1


    df=pd.DataFrame.from_dict(edgetable,orient='index')
    #df=pd.DataFrame(columns=['auth_wikidataid','auth_fio_short','dest_wikidataid','dest_fio_short','weight','auth_ideol','dest_ideol'])
    # with open(outfile, 'w', encoding='utf-8', newline='') as outfile:
    #     fieldnames = ['auth_wikidataid', 'dest_wikidataid', 'auth_fio_short', 'dest_fio_short', 'weight']
    #     writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
    #     writer.writeheader()
    #     for edge_id, edge in edgetable.items():
    #         edge['auth_fio_short'] = mapping[edge['auth_wikidataid']]
    #         edge['dest_fio_short'] = mapping[edge['dest_wikidataid']]
    #         writer.writerow(edge)
    writer = PajekWriter(df,
                     directed=True,
                     weighted=True,
                     citing_colname="auth_fio_short",
                     cited_colname="dest_fio_short",
                     weight_colname="weight",
                     citing_cluster_colname="auth_ideol",
                     cited_cluster_colname="dest_ideol")
    writer.write(outfile_net)
    writer.writecluster(outfile_clu)

if __name__ == '__main__':
    main()
