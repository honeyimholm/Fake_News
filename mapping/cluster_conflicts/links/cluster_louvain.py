import os
import json
from codecs import open
from time import time
from settings import API_KEY, DATA_FOLDER, RAW_FOLDER
import numpy as np
from sklearn.preprocessing import normalize
from scipy.sparse import csc_matrix

import community
import networkx as nx

from cluster_directed_links import links_to_matrix, transform_matrix, time_step

LINKS_FILE = os.path.join(DATA_FOLDER, 'indexed_links.json')
FINAL_INDEX_FILE = os.path.join(DATA_FOLDER, 'final_index.json')
REVERSE_INDEX_FILE = os.path.join(DATA_FOLDER, 'reverse_index.json')
CONFLICT_SCORES = os.path.join(DATA_FOLDER, 'Nscores.json')
CLUSTER_FILE = os.path.join(DATA_FOLDER, 'louvain_clusters.json')

PERCENTILE = 98
MARKOV_TIME = 0.88


if __name__ == '__main__':

    t_start = time()

    scores = json.load(open(CONFLICT_SCORES))
    threshold = np.percentile(list(scores.values()), PERCENTILE)
    print(threshold)
    conflicts = [article for article in scores if scores[article] > threshold]
    print(len(conflicts))
    print(sorted([(article, score) for article, score in scores.items() if score > threshold], key=lambda x: x[1]))
    wars = sorted([k for k in conflicts], key=lambda x: scores[x], reverse=True)

    index = json.load(open(FINAL_INDEX_FILE))
    index = {k: index[k] for k in wars if k in index}
    wars = [index[item] for item in wars if item in index]
    filter_index = {k: i for i, k in enumerate(wars)}
    reverse_index = {filter_index[v]: k for k, v in index.items()}

    wars_links = json.load(open(LINKS_FILE))
    link_matrix = links_to_matrix(wars_links)
    print('link matrix created')
    secondary_matrix = transform_matrix(link_matrix, wars, directed=True)
    print('link matrix transformed')
    print(max(secondary_matrix.data))

    agreement_graph = nx.from_scipy_sparse_matrix(secondary_matrix, create_using=nx.Graph())
    # agreement_graph = agreement_graph.to_undirected()
    clustering = community.best_partition(agreement_graph, resolution=0.3)
    nx.set_node_attributes(agreement_graph, name='cluster', values=clustering)
    nx.set_node_attributes(agreement_graph, name='title', values=reverse_index)

    weird_cluster = ['Europe', "Martina Stoessel", "Lodovica Comello", "Violetta (série télévisée)", "Forex", "Jorge Blanco (acteur)"]
    for title in weird_cluster:

        print(title)
        print(len(agreement_graph[filter_index[index[title]]]))
        print([(reverse_index[idx], item['weight']) for idx, item in agreement_graph[filter_index[index[title]]].items() if reverse_index[idx] in weird_cluster])

    print(clustering)

    named_clusters = []
    for node, cluster in clustering.items():
        if cluster == len(named_clusters):
            named_clusters.append([reverse_index[node]])
        else:
            named_clusters[cluster].append(reverse_index[node])

    named_clusters.sort(key=len, reverse=True)
    print(named_clusters)
    print(len(named_clusters))

    json.dump(named_clusters, open(CLUSTER_FILE, 'w'), indent=2, ensure_ascii=False)
    print('clusters dumped')
    current_time = time_step(t_start)
