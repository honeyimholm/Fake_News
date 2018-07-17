import os
import json
import scipy.sparse as sp
import numpy as np
from codecs import open
import networkx as nx
import community
import randomcolor
import matplotlib.pyplot as plt

from settings import DATA_FOLDER

LINKS_FILE = os.path.join(DATA_FOLDER, '2110_symmetrized_links.json')
ADJACENCY_MATRIX = os.path.join(DATA_FOLDER, '2110_conflict_adjacency.txt.npz')
MATRIX_INDEX = os.path.join(DATA_FOLDER, '2110_conflict_matrix_index.txt')
TALK_DATA_FILE = os.path.join(DATA_FOLDER, '2110_talk_data.json')
CONTROVERSY_SCORES = os.path.join(DATA_FOLDER, '2110_controversy_scores.txt')


def load_sparse_csr(filename):
    loader = np.load(filename)
    return sp.csr_matrix(([max(0, value - 0.1) for value in loader['data']], loader['indices'], loader['indptr']), shape=loader['shape'])


if __name__ == '__main__':
    adjacency_matrix = load_sparse_csr(ADJACENCY_MATRIX)
    adjacency_matrix.eliminate_zeros()
    print(adjacency_matrix.shape)
    print(len(adjacency_matrix.data))
    g = nx.from_scipy_sparse_matrix(adjacency_matrix)
    index = json.load(open(MATRIX_INDEX, 'r', encoding='utf-8'), encoding='utf8')
    clustering = community.best_partition(g)

    rand_color = randomcolor.RandomColor()
    cluster_colors = [rand_color.generate() for _ in set(clustering.values())]
    nx.set_node_attributes(g, name="title", values={k: index[k] for k in g.nodes()})
    node_colors = [cluster_colors[clustering[node]] for node in g.nodes()]

    pos = nx.spring_layout(g)
    nx.draw_networkx_nodes(g, pos=pos, node_color=node_colors)
    nx.draw_networkx_edges(g, pos=pos)
    nx.draw_networkx_labels(g,pos)

    plt.title("Conflict graph")
    plt.axis('off')
    plt.savefig('output.png')
    plt.show()
