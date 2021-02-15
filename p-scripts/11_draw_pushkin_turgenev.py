import logging
import time
import sys
import csv
import argparse
import networkx as nx
import matplotlib.pyplot as plt
from math import sqrt

#%config InlineBackend.figure_format = 'svg'
#plt.rcParams['figure.figsize'] = (10, 6)

# Логирование в utf-8 для отладки
logging.basicConfig(
    handlers=[logging.StreamHandler(sys.stdout)], level=logging.INFO)

def cm_to_inch(value):
    return value/2.54

def main():
    parser = argparse.ArgumentParser(prog='Fill nodes and edges', description='Fill nodes and edges')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                    help='csv file for processing', default="../data/muratova_edgelist.csv")
    parser.add_argument('infile2',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                    help='csv file 2 for processing', default="../data/persons_table_wikidata.csv")
    args = parser.parse_args()
    infile_data = args.infile.name
    infile2_data = args.infile2.name
    
    edgelist = []
    with open(infile_data, newline='', encoding='utf-8') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        for line in reader:
            edgelist.append(line)

    ptable = []
    with open(infile2_data, newline='', encoding='utf-8') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        for line in reader:
            ptable.append(line)

    mapping = {}
    for line in ptable:
        mapping[line["wikidata_id"]] = line["fio_short"]

    G = nx.Graph()
    for edge in edgelist:
        G.add_edge(edge['auth_fio_short'], edge['dest_fio_short'], weight=int(edge['weight']))

    # no need to relabel, we now read names directly from the input edgelist
    # G = nx.relabel_nodes(G, mapping)

    colors = range(20)
    #edges0,weights0 = zip(*nx.get_edge_attributes(G,'weight').items())

    options = {
        "node_color": "#A0CBE2",
        "edge_color": "#6de5f7",
        "font_color": "#A52A2A",
        "width": 1,
        "edge_cmap": plt.cm.Blues,
        "with_labels": True,
        "font_weight": "bold",
        #"edge_color": weights0
    }
    #plt.subplot(122)
    plt.figure(figsize=(cm_to_inch(100),cm_to_inch(100)), dpi=200)

    paths_edges=nx.all_simple_edge_paths(G,mapping['Q7200'], mapping['Q42831'], cutoff=3)
    H = nx.Graph()
    for edge in paths_edges:
        H.add_edges_from(edge)

    #H = G.subgraph(next(nx.connected_components(G)))
    degree = G.degree()
    to_remove = [n for (n,deg) in degree if deg <= 1]
    while to_remove:
        G.remove_nodes_from(to_remove)
        degree = G.degree()
        to_remove = [n for (n,deg) in degree if deg <= 1]
    #paths=nx.all_simple_paths(G,"Пушкин, А. С.", "Тургенев, И.С.", cutoff=3)
    #print(list(paths))
    #for path in map(nx.utils.pairwise, paths):
    #    for u,v in path:
    #        G[u][v]["weight"]=2
  
    initialpos = {mapping['Q7200']:(-200,-200), mapping['Q42831']:(200,200)}
    betweennessCentrality = nx.betweenness_centrality(G,normalized=True, endpoints=True)
    node_size =  [v * 10000 for v in betweennessCentrality.values()]
    pos = nx.spring_layout(G, seed=367, iterations=300, pos = initialpos, k=70/sqrt(len(G)))
    #pos = nx.spring_layout(H, seed=367, iterations=300, pos = initialpos)#, k=10/sqrt(len(G)))
    #pos = nx.kamada_kawai_layout(G)
    #pos = nx.spectral_layout(G)
    nx.draw_networkx(G, pos=pos, node_size=node_size, **options)
    #nx.draw(H, pos, **options)
    plt.savefig("Graph.svg", format="svg", bbox_inches='tight')
    #print(G)

if __name__ == '__main__':
    main()
