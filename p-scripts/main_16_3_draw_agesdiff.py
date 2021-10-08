import logging
import time
import sys
import csv
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from math import sqrt
import community
from datetime import datetime

# удаляются все ноды с 1 связью или оставшиеся без связей
# граф строится с делением по группам
# цвет связей означает степерь разницы в возрасте

#%config InlineBackend.figure_format = 'svg'
#plt.rcParams['figure.figsize'] = (10, 6)

default_edgelist_file = '../data/muratova_edgelist_res15.csv'
default_persons_file = '../data/persons_table_res13.csv'
default_dest_file = "Graph_16_3_"+datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+".png"

# Логирование в utf-8 для отладки
logging.basicConfig(
    handlers=[logging.StreamHandler(sys.stdout)], level=logging.INFO)

def safe_list_get(l, idx, default):
    try:
        return l[idx]
    except:
        return default    

def cm_to_inch(value):
    return value/2.54


def community_layout(g, partition):
    """
    Compute the layout for a modular graph.


    Arguments:
    ----------
    g -- networkx.Graph or networkx.DiGraph instance
        graph to plot

    partition -- dict mapping int node -> int community
        graph partitions


    Returns:
    --------
    pos -- dict mapping int node -> (float x, float y)
        node positions

    """

    pos_communities = _position_communities(g, partition, scale=2., k=40/sqrt(len(g)), seed=999, iterations=10)

    pos_nodes = _position_nodes(g, partition, scale=1.5, k=30/sqrt(len(g)), seed=999, iterations=10)

    # combine positions
    pos = dict()
    for node in g.nodes():
        pos[node] = pos_communities[node] + pos_nodes[node]

    return pos

def _position_communities(g, partition, **kwargs):

    # create a weighted graph, in which each node corresponds to a community,
    # and each edge weight to the number of edges between communities
    between_community_edges = _find_between_community_edges(g, partition)

    communities = set(partition.values())
    hypergraph = nx.DiGraph()
    hypergraph.add_nodes_from(communities)
    for (ci, cj), edges in between_community_edges.items():
        hypergraph.add_edge(ci, cj, weight=len(edges))

    # find layout for communities
    pos_communities = nx.spring_layout(hypergraph, **kwargs)

    # set node positions to position of community
    pos = dict()
    for node, community in partition.items():
        pos[node] = pos_communities[community]

    return pos

def _find_between_community_edges(g, partition):

    edges = dict()

    for (ni, nj) in g.edges():
        ci = partition[ni]
        cj = partition[nj]

        if ci != cj:
            try:
                edges[(ci, cj)] += [(ni, nj)]
            except KeyError:
                edges[(ci, cj)] = [(ni, nj)]

    return edges

def _position_nodes(g, partition, **kwargs):
    """
    Positions nodes within communities.
    """

    communities = dict()
    for node, community in partition.items():
        try:
            communities[community] += [node]
        except KeyError:
            communities[community] = [node]

    pos = dict()
    for ci, nodes in communities.items():
        subgraph = g.subgraph(nodes)
        pos_subgraph = nx.spring_layout(subgraph, **kwargs)
        pos.update(pos_subgraph)

    return pos

def main():
    parser = argparse.ArgumentParser(prog='Fill nodes and edges', description='Fill nodes and edges')
    parser.add_argument('infile',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
                    help='csv file for processing', default=default_edgelist_file)
    # parser.add_argument('infile2',  type=argparse.FileType('r', encoding='utf-8'), nargs='?',
    #                 help='csv file 2 for processing', default="../data/persons_table_wikidata.csv")
    args = parser.parse_args()
    infile_data = args.infile.name
    # infile2_data = args.infile2.name
    
    edgelist = []
    with open(infile_data, newline='', encoding='utf-8') as datafile:
        reader = csv.DictReader(datafile, delimiter=';')
        for line in reader:
            edgelist.append(line)

    # ptable = []
    # with open(infile2_data, newline='', encoding='utf-8') as datafile:
    #     reader = csv.DictReader(datafile, delimiter=';')
    #     for line in reader:
    #         ptable.append(line)

    # mapping = {}
    # for line in ptable:
    #     mapping[line["wikidata_id"]] = line["fio_short"]

    G = nx.Graph()
    for edge in edgelist:
        if edge['auth_birthdate'] != '-1' and edge['dest_birthdate'] != '-1':
            G.add_edge(edge['auth_fio_short'], edge['dest_fio_short'], 
                weight=int(edge['weight']), 
                agediff=int(edge['age_diff']), 
            )
            G.nodes[edge['auth_fio_short']]['birthdate']=int(edge['auth_birthdate'])
            G.nodes[edge['dest_fio_short']]['birthdate']=int(edge['dest_birthdate'])

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
    plt.axis('off')
    plt.figure(figsize=(cm_to_inch(100),cm_to_inch(100)), dpi=200)

    #paths_edges=nx.all_simple_edge_paths(G,mapping['Q7200'], mapping['Q42831'], cutoff=3)
    #H = nx.Graph()
    #for edge in paths_edges:
    #    H.add_edges_from(edge)

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
  
    #initialpos = {mapping['Q7200']:(-250,-250), mapping['Q42831']:(250,250)}
    betweennessCentrality = nx.betweenness_centrality(G,normalized=True, endpoints=True)
    node_size =  [v * 10000 for v in betweennessCentrality.values()]
    #pos = nx.spring_layout(G, seed=367, iterations=300, pos = initialpos, k=70/sqrt(len(G)))
    #pos = nx.spring_layout(H, seed=367, iterations=300, pos = initialpos)#, k=10/sqrt(len(G)))
    #pos = nx.kamada_kawai_layout(G)
    #pos = nx.spectral_layout(G)
    partition = community.best_partition(G, random_state=367, resolution=3)
    ###pos = nx.spring_layout(G, seed=367, iterations=300, pos = initialpos, k=90/sqrt(len(G)))
    pos = community_layout(G, partition)
    #nx.draw_networkx(G, pos=pos, node_size=node_size, **options)
    #nx.draw(H, pos, **options)

    weights = [G[u][v]['weight']/15 for u,v in G.edges()]
    edgecolor = [G[u][v]['agediff'] if G[u][v]['agediff'] > 4 else 0 for u,v in G.edges()]
    # edgecolor=[]
    # for u,v in G.edges():
    #     if G[u][v]['agediff']>=0 and G[u][v]['agediff'] < 6:
    #         edgecolor.append(1)
    #     elif G[u][v]['agediff']>5 and G[u][v]['agediff'] < 11:
    #         edgecolor.append(2)
    #     elif G[u][v]['agediff']>10 and G[u][v]['agediff'] < 16:
    #         edgecolor.append(3)
    #     elif G[u][v]['agediff']>15 and G[u][v]['agediff'] < 21:
    #         edgecolor.append(4)
    #     elif G[u][v]['agediff']>20:
    #         edgecolor.append(5)

    #c = cm.Set1(5, alpha=1)
    nodes_colors = {}
    labels={}
    for node in G.nodes():
        if betweennessCentrality[node] >= 0.005:
            labels[node]=node
    for node in G.nodes():
        nodes_colors[node] = G.nodes[node]['birthdate']
    for u,v,a in G.edges(data=True):
        if a['weight'] > 10 or u==v:
            labels[u] = u
            labels[v] = v
    #nx.draw_networkx_edges(G, pos, alpha=0.45, width=weights, edge_color='k')
    #edges = nx.draw_networkx_edges(G, pos, alpha=0.45, width=weights, edge_cmap=plt.cm.cool, edge_vmin=0, edge_vmax=10, edge_color=edgecolor)
    #edges = nx.draw_networkx_edges(G, pos, alpha=0.6, width=weights, edge_cmap=cm.tab10, edge_color=edgecolor)
    #nx.draw_networkx_nodes(G, pos, node_size=node_size, cmap=plt.cm.viridis, node_color=list(nodes_colors.values()))
    #nx.draw_networkx_nodes(G, pos, node_size=node_size, cmap=plt.cm.viridis, node_color=list(partition.values()))
    #nodes = nx.draw_networkx_nodes(G, pos, node_size=node_size, cmap=plt.cm.tab20, node_color=list(nodes_colors.values()))
    #nx.draw_networkx_labels(G, pos, labels, font_weight="bold", horizontalalignment="left", verticalalignment='top', font_color= "#ff2f00")
    #plt.colorbar(edges, fraction=0.05)
    #plt.colorbar(nodes)

    edges = nx.draw_networkx_edges(G, pos, alpha=0.6, width=weights, edge_cmap=cm.tab10, edge_color=edgecolor)
    nx.draw_networkx_nodes(G, pos, node_size=node_size, cmap=plt.cm.viridis, node_color=list(partition.values()))
    nx.draw_networkx_labels(G, pos, labels, font_weight="bold", horizontalalignment="left", verticalalignment='top', font_color= "#ff2f00")
    plt.colorbar(edges)
    plt.savefig('agediff_'+default_dest_file, format="png", bbox_inches='tight')
    plt.clf()
    nx.draw_networkx_edges(G, pos, alpha=0.45, width=weights, edge_color='k')
    nodes = nx.draw_networkx_nodes(G, pos, node_size=node_size, cmap=plt.cm.tab20, node_color=list(nodes_colors.values()))
    nx.draw_networkx_labels(G, pos, labels, font_weight="bold", horizontalalignment="left", verticalalignment='top', font_color= "#ff2f00")
    plt.colorbar(nodes)
    plt.savefig('birthdates_'+default_dest_file, format="png", bbox_inches='tight')
    #print(G)

if __name__ == '__main__':
    main()
