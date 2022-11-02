#!/usr/bin/env python
# coding: utf-8
import runpy
import argparse

run_sequence=[
"main_01_uniqid.py",
"main_02_author_extract_commadot.py",
"main_03_author_spllit_prim.py",
"main_05_author_extract_io.py",
"main_06_adresat_extract_commadot.py",
"main_07_adresat_split_prim.py",
"main_08_adresat_extract_commas.py",
"main_09_adresat_extract_io.py",
"main_10_adresat_pymorphy_to_single.py",
"main_11_create_update_persons_table.py",
"main_12_persons_table_wikidata_ids.py",
"main_13_persons_table_wikidata_dates.py",
"main_14_insert_wikidata_to_csv.py",
"main_15_fill_nodes_edges.py"
]

def main():
    parser = argparse.ArgumentParser(prog='seq run scripts 01-15',
                                     description='seq run scripts 01-15')
    parser.add_argument('startfile',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                        help='csv file for processing', default='../data/20221001_muratova_with_letters_numbers.csv')

    args = parser.parse_args()
    startfile = args.startfile.name

    for idx,name in enumerate(run_sequence):
        # if idx == 0 and startfile:
        #     runpy.run_path("%s %s" % (name, startfile))
        # else:
        runpy.run_path(name, run_name='__main__')

if __name__ == '__main__':
    main()