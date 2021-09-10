import logging
import sys
import csv
import argparse

#%config InlineBackend.figure_format = 'svg'
#plt.rcParams['figure.figsize'] = (10, 6)

# Логирование в utf-8 для отладки
logging.basicConfig(
    handlers=[logging.StreamHandler(sys.stdout)], level=logging.INFO)

def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default

def main():
    parser = argparse.ArgumentParser(prog='Fill nodes and edges', description='Fill nodes and edges')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                    help='csv file for processing', default="../data/muratova_finished.csv")
    parser.add_argument('infile2',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                    help='csv file 2 for processing', default="../data/persons_table_wikidata_dates.csv")
    parser.add_argument('outfile',  type=argparse.FileType('w', encoding='utf-8'), nargs='?',
                    help='output file', default="../data/muratova_edgelist_agediff.csv")
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
        mapping[line["wikidata_id"]]={}
        mapping[line["wikidata_id"]]["fio"] = line["fio_short"]
        mapping[line["wikidata_id"]]["birthdate"] = safe_cast(line["wikidata_birthdate"], int)

    edgetable = {}
    for line in ltable:
        if not line['auth_wikidataid'] or not line['dest_wikidataid']:
            continue
        if 'еизвест' in line["адресатИП"] or 'еустановл' in line["адресатИП"]:
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

    with open(outfile, 'w', encoding='utf-8') as outfile:
        fieldnames = ['auth_wikidataid', 'dest_wikidataid', 'auth_fio_short', 'dest_fio_short', 'weight', 'age_diff']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for edge_id, edge in edgetable.items():
            edge['auth_fio_short'] = mapping[edge['auth_wikidataid']]["fio"]
            edge['dest_fio_short'] = mapping[edge['dest_wikidataid']]["fio"]
            if mapping[edge['auth_wikidataid']]["birthdate"] and mapping[edge['dest_wikidataid']]["birthdate"]:
                edge['age_diff'] = abs(mapping[edge['auth_wikidataid']]["birthdate"] - mapping[edge['dest_wikidataid']]["birthdate"])
            else:
                edge['age_diff'] = 16777215
            writer.writerow(edge)


if __name__ == '__main__':
    main()
