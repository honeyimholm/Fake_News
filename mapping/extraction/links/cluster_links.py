import os
import pickle
import json
from codecs import open
from time import time

from mapping.infomap import infomap

from settings import DATA_FOLDER


INDEXED_LINKS_FILE = os.path.join(DATA_FOLDER, '2110_reindexed_pruned_links.json')
REVERSE_INDEX_FILE = os.path.join(DATA_FOLDER, '2110_reverse_reindex.json')
HIERARCHICAL_CLUSTER_FILE = os.path.join(DATA_FOLDER, '2110_hierarchical_clusters.json')


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
    t_start = time()
    clusterer = infomap.Infomap(str("--undirected  --zero-based-numbering  --tune-iteration-threshold  1e-5 --markov-time 1"))
    indexed_citations = json.load(open(INDEXED_LINKS_FILE, 'r'))
    for article, citations in indexed_citations.items():
        for citation in citations:
            clusterer.addLink(int(article), citation)
    print('network built')
    clusterer.run()
    tree = clusterer.tree
    print('clusters built')
    current_time = time_step(t_start)

    reverse_index = json.load(open(REVERSE_INDEX_FILE, 'r', encoding='utf8'))
    hierarchical_clusters = []
    t0 = time()
    current_upper_cluster = 0
    for i, node in enumerate(tree.treeIter()):
        if node.isLeaf:
            current_list = hierarchical_clusters
            for index in node.path()[:-1]:
                try:
                    current_list = current_list[index]
                except IndexError:
                    current_list.append([])
                    current_list = current_list[-1]
            current_list.append(reverse_index[str(node.data.name)])
            if node.path()[0] != current_upper_cluster:
                current_upper_cluster = node.path()[0]

    recursive_sort(hierarchical_clusters)

    json.dump(hierarchical_clusters, open(HIERARCHICAL_CLUSTER_FILE, 'w'), indent=2)
    print('clusters dumped')
    current_time = time_step(t_start)