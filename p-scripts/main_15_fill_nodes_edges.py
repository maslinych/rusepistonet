import logging
import sys
import csv
import argparse
import re

# сохраняем в отдельный файлы сформированные грани и ноды для графа

#%config InlineBackend.figure_format = 'svg'
#plt.rcParams['figure.figsize'] = (10, 6)

default_source_file = '../data/muratova_res14.csv'
default_persons_file = '../data/persons_table_res13.csv'
default_dest_file = '../data/muratova_edgelist_res15.csv'

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
    parser.add_argument('outfile',  type=argparse.FileType('w', encoding='utf-8'), nargs='?',
                    help='output file', default=default_dest_file)
    args = parser.parse_args()
    infile_data = args.infile.name
    infile2_data = args.infile2.name
    outfile = args.outfile.name

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

    edgetable = {}
    for line in ltable:
        if not line['auth_wikidataid'] or not line['dest_wikidataid']:
            continue
        if  any(re.search(x,line["адресатИП"],re.IGNORECASE) for x in exclude_list):
            continue
        edge = line['auth_wikidataid']+line['dest_wikidataid']
        rev_edge = line['dest_wikidataid']+line['auth_wikidataid']
        if edge not in edgetable.keys() and rev_edge not in edgetable.keys():
            edgetable[edge] = {}
            edgetable[edge]['auth_wikidataid'] = line['auth_wikidataid']
            edgetable[edge]['dest_wikidataid'] = line['dest_wikidataid']
            edgetable[edge]['weight']=1
            #if line['dest_wikidataid'] in ['Q7200','Q42831']:
            #    edgetable[edge]['weight']=5
            #if line['auth_wikidataid'] in ['Q7200','Q42831']:
            #    edgetable[edge]['weight']=5
            #edgetable[edge]['freq']=1
        elif edge in edgetable.keys():
                edgetable[edge]['weight']=edgetable[edge]['weight']+1
        elif rev_edge in edgetable.keys():
                edgetable[rev_edge]['weight']=edgetable[rev_edge]['weight']+1
    # print(edgetable)

    with open(outfile, 'w', encoding='utf-8', newline='') as outfile:
        fieldnames = ['auth_wikidataid', 'dest_wikidataid', 'auth_fio_short', 'dest_fio_short', 'weight']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for edge_id, edge in edgetable.items():
            edge['auth_fio_short'] = mapping[edge['auth_wikidataid']]
            edge['dest_fio_short'] = mapping[edge['dest_wikidataid']]
            writer.writerow(edge)


if __name__ == '__main__':
    main()
