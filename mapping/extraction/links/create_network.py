import os
import pickle
import json
from codecs import open
from time import time
import randomcolor
import deepwalk
import numpy as np
import scipy.sparse as sp

import networkx as nx

from settings import DATA_FOLDER


INDEXED_LINKS_FILE = os.path.join(DATA_FOLDER, '2110_reindexed_pruned_links.json')
REVERSE_INDEX_FILE = os.path.join(DATA_FOLDER, '2110_reverse_reindex.json')
HIERARCHICAL_CLUSTER_FILE = os.path.join(DATA_FOLDER, '2110_hierarchical_clusters.json')
TITLE_TO_PATH_FILE = os.path.join(DATA_FOLDER, '2110_title_to_path.json')
DEGREES_FILE = os.path.join(DATA_FOLDER, '2110_degrees.json')
EIGENVECTOR_FILE = os.path.join(DATA_FOLDER, '2110_eigenvectors.json')
GRAPH_FILE = os.path.join(DATA_FOLDER, '2110_graph.txt')
ADJACENCY_MATRIX = os.path.join(DATA_FOLDER, '2110_adjacency.txt')


load = False


def save_sparse_csr(filename, matrix):
    np.savez(filename, data = matrix.data, indices=matrix.indices,
             indptr =matrix.indptr, shape=matrix.shape)


def time_step(current_time):
    print(str(time() - current_time) + 's elapsed')
    return time()


def total_elements(nested_list):
    if hasattr(nested_list, '__iter__'):
        return sum([total_elements(item) for item in nested_list])
    else:
        return 1


def recursive_sort(nested_list):
    if hasattr(nested_list, '__iter__'):
        nested_list.sort(key=total_elements, reverse=True)
        for item in nested_list:
            recursive_sort(item)
    else:
        return None


if __name__ == '__main__':
    reverse_index = json.load(open(REVERSE_INDEX_FILE, 'r', encoding='utf8'), encoding='utf8')
    indexed_citations = json.load(open(INDEXED_LINKS_FILE, 'r'))
    t_start = time()

    if load:
        g = nx.read_edgelist(GRAPH_FILE)
    else:
        title_to_path = json.load(open(TITLE_TO_PATH_FILE, 'r'))
        g = nx.Graph()
        g.add_nodes_from([(index, {'title': title, 'cluster': title_to_path[title][0]}) for index, title in reverse_index.items() if title])
        print('nodes added in ' + str(time() - t_start))
        for article, citations in indexed_citations.items():
            g.add_edges_from([(article, citation) for citation in citations])
        print('network built in ' + str(time() - t_start))
        nx.write_edgelist(g, GRAPH_FILE)
        print('network dumped in ' + str(time() - t_start))

    sparse_adjacency = nx.to_scipy_sparse_matrix(g)
    save_sparse_csr(ADJACENCY_MATRIX, sparse_adjacency)


    # degree_centralities = nx.degree_centrality(g)
    # degree_centralities = {reverse_index[str(node)]: degree for node, degree in degree_centralities.iteritems()}
    # json.dump(degree_centralities, open(DEGREES_FILE, 'w', encoding='utf8'), indent=2, encoding='utf8', ensure_ascii=False)
    # print 'degrees built in ' + str(time() - t_start)

    # rand_color = randomcolor.RandomColor()
    # hierarchical_clusters = json.load(open(HIERARCHICAL_CLUSTER_FILE, 'r'))
    #
    # print g.nodes(data=True)
    # cluster_colors = [rand_color.generate() for _ in range(len(hierarchical_clusters))]
    # node_colors = [cluster_colors[node[1]['cluster']] if node[1] else rand_color.generate() for node in g.nodes(data=True)]
    #
    # nx.draw_networkx(g, node_color=node_colors)



    # eigenvector_centralities = nx.eigenvector_centrality(g)
    # eigenvector_centralities = {reverse_index[str(node)]: degree for node, degree in eigenvector_centralities.iteritems()}
    # json.dump(eigenvector_centralities, open(EIGENVECTOR_FILE, 'w', encoding='utf8'), indent=2, encoding='utf8', ensure_ascii=False)
    # print 'eigenvectors built in ' + str(time() - t_start)