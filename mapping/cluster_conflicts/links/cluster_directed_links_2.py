import os
import json
from codecs import open
from time import time
from settings import API_KEY, DATA_FOLDER, RAW_FOLDER
import numpy as np
from sklearn.preprocessing import normalize
from scipy.sparse import csc_matrix
import itertools

from mapping.infomap import infomap

LINKS_FILE = os.path.join(DATA_FOLDER, 'indexed_links.json')
FINAL_INDEX_FILE = os.path.join(DATA_FOLDER, 'final_index.json')
REVERSE_INDEX_FILE = os.path.join(DATA_FOLDER, 'reverse_index.json')
CONFLICT_SCORES = os.path.join(DATA_FOLDER, 'Nscores.json')
HIERARCHICAL_CLUSTER_FILE = os.path.join(DATA_FOLDER, 'hierarchical_clusters.json')

FIRST_PERCENTILE = 98
SECOND_PERCENTILE = 98
MARKOV_TIME = 0.85


def time_step(current_time):
    print(str(time() - current_time) + 's elapsed')
    return time()


def total_elements(nested_list):
    if isinstance(nested_list, list):
        return sum([total_elements(item) for item in nested_list])
    else:
        return 1


def recursive_sort(nested_list):
    if isinstance(nested_list, list):
        nested_list.sort(key=total_elements, reverse=True)
        for item in nested_list:
            recursive_sort(item)
    else:
        return None


def iterate_through_tree(nested_list, path=None):
    if path is None:
        path = tuple()
    if isinstance(nested_list, list):
        for i, sublist in enumerate(nested_list):
            subpath = path + (i,)
            for item in iterate_through_tree(sublist, subpath):
                yield item
    else:
        yield nested_list, path


def collect_elements(nested_list):
    if isinstance(nested_list, list):
        return list(itertools.chain(*[collect_elements(bird) for bird in nested_list]))
    else:
        return [nested_list]


def collect_titles(nested_list):
    return [article['title'] for article in collect_elements(nested_list)]


def controversy_mean(nested_list):
    elements = collect_elements(nested_list)
    return np.mean([element['score'] for element in elements])


def links_to_matrix(link_dict):
    n = max([int(i) for i in link_dict.keys()])

    indptr = [0] + [len(set(link_dict.get(str(i), []))) for i in range(n)]
    indptr = list(np.cumsum(indptr))
    data = np.ones(indptr[-1])
    indices = [j for i in range(n) for j in set(link_dict.get(str(i), []))]

    n = max(n, max(indices) + 1)

    for _ in range(len(indptr), n + 1):
        indptr.append(indptr[-1])

    link_matrix = csc_matrix((data, indices, indptr), shape=(n, n))

    return link_matrix


def transform_matrix(link_matrix, articles_of_interest, directed=True):
    start_time = time()

    H = link_matrix[:, articles_of_interest]

    if directed:
        W = link_matrix[articles_of_interest, :]
    else:
        W = H.transpose()

    # H = normalize(H, norm='l1', axis=0)
    # W = normalize(W, norm='l1', axis=1)

    print('matrix normalization time : {}'.format(time() - start_time))

    WH = W.dot(H)
    filter_sparse(WH, 95)
    WH = normalize(WH, norm='l2', axis=1)

    X = link_matrix[:, articles_of_interest]
    X = X[articles_of_interest, :]

    print('matrix transformation time : {}'.format(time() - start_time))

    return X + WH
    # return normalize(X + WH, norm='l1', axis=1)


def filter_sparse(matrix, percentile):
    threshold = np.percentile(matrix.data, percentile)
    matrix.data = np.array([value if value > threshold else 0 for value in matrix.data])
    matrix.eliminate_zeros()


def matrix_to_infomap(matrix, clusterer):
    matrix = csc_matrix(matrix)

    for i in range(len(matrix.indptr) - 1):
        for j in range(matrix.indptr[i], matrix.indptr[i + 1]):
            clusterer.addLink(int(i), int(matrix.indices[j]), matrix.data[j])


def collect_conflicts(nested_list, threshold):
    return [article for article in collect_elements(nested_list) if article['score'] > threshold]


if __name__ == '__main__':

    t_start = time()

    scores = json.load(open(CONFLICT_SCORES))
    first_threshold = np.percentile(list(scores.values()), FIRST_PERCENTILE)
    second_threshold = np.percentile(list(scores.values()), SECOND_PERCENTILE)
    print(second_threshold)
    articles_to_cluster = [article for article in scores if scores[article] > first_threshold]
    print(
        sorted([(article, score) for article, score in scores.items() if score > first_threshold], key=lambda x: x[1]))
    print(len(articles_to_cluster))
    wars = sorted([k for k in articles_to_cluster], key=lambda x: scores[x], reverse=True)

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

    clusterer = infomap.Infomap(
        str("--directed --two-level --zero-based-numbering --tune-iteration-threshold  1e-5 --markov-time {}".format(
            MARKOV_TIME)))
    matrix_to_infomap(secondary_matrix, clusterer)
    indexed_citations = wars_links
    print('network built')
    clusterer.run()
    tree = clusterer.tree
    print('clusters built')
    current_time = time_step(t_start)

    hierarchical_clusters = []
    t0 = time()
    current_upper_cluster = 0
    missing = 0
    for i, node in enumerate(tree.treeIter()):
        if node.isLeaf:
            current_list = hierarchical_clusters
            for index in node.path()[:-1]:
                try:
                    current_list = current_list[index]
                except IndexError:
                    current_list.append([])
                    current_list = current_list[-1]
            try:
                title = reverse_index[int(node.data.name)]
                score = scores[title]
                if score > second_threshold:
                    current_list.append({'index': int(node.data.name), 'title': title, 'score': scores[title]})
            except KeyError:
                missing += 1
                print(node.data.name)
                print(len(reverse_index.keys()))
                print()
            if node.path()[0] != current_upper_cluster:
                current_upper_cluster = node.path()[0]

    n = total_elements(hierarchical_clusters)
    recursive_sort(hierarchical_clusters)

    print('now filtering')
    current_time = time_step(t_start)

    element_count = 0
    indices = []
    indptr = [0]
    data = []
    remaining_items = {}

    midway = 0
    for cluster in hierarchical_clusters:

        if element_count < n // 2:
            cluster_size = total_elements(cluster)
            element_count += cluster_size
            indptr.append(indptr[-1] + cluster_size)
            data.extend([1 / float(cluster_size)] * cluster_size)
            indices.extend([item['index'] for item in cluster])
            midway += 1

        else:
            for item in cluster:
                remaining_items[item['index']] = item

    second_half_indices = sorted([item['index'] for i in range(midway, len(hierarchical_clusters)) for item in hierarchical_clusters[i]])
    second_half_reverse_indices = {k: v for v, k in enumerate(second_half_indices)}
    first_half_indices = list(set(indices))
    first_half_reverse_indices = {k: v for v, k in enumerate(first_half_indices)}

    hierarchical_clusters = hierarchical_clusters[:midway]
    for _ in range(len(hierarchical_clusters)):
        hierarchical_clusters.append([])

    readded = 0

    for i, second_half_index in enumerate(second_half_indices):

        secondary_matrix = secondary_matrix[first_half_indices + second_half_indices, :]
        secondary_matrix = secondary_matrix[:, first_half_indices + second_half_indices]
        secondary_matrix = secondary_matrix.todense()
        print(secondary_matrix[second_half_reverse_indices[second_half_index], [first_half_reverse_indices[item['index']] for item in hierarchical_clusters[0]]])
        print('matrix')
        cluster_scores = [np.median(secondary_matrix[second_half_reverse_indices[second_half_index], [first_half_reverse_indices[item['index']] for item in cluster]]) for cluster in hierarchical_clusters]
        cluster_of_choice = np.argmax(cluster_scores)
        max_score = np.max(cluster_scores)

        if max_score > 0:
            hierarchical_clusters[cluster_of_choice + midway].append(remaining_items[second_half_index])
            readded += 1

    print(readded)

    json.dump(hierarchical_clusters, open(HIERARCHICAL_CLUSTER_FILE, 'w'), ensure_ascii=False, indent=2)
    print('clusters dumped')
    current_time = time_step(t_start)
