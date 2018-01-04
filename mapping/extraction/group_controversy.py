import os
import json
import scipy.sparse as sp
import numpy as np
from codecs import open

from settings import DATA_FOLDER

LINKS_FILE = os.path.join(DATA_FOLDER, '2110_symmetrized_links.json')
ADJACENCY_MATRIX = os.path.join(DATA_FOLDER, '2110_adjacency.txt')
TALK_DATA_FILE = os.path.join(DATA_FOLDER, '2110_talk_data.json')
CONTROVERSY_SCORES = os.path.join(DATA_FOLDER, '2110_controversy_scores.txt')


def load_sparse_csr(filename):
    loader = np.load(filename)
    return sp.csr_matrix((loader['data'], loader['indices'], loader['indptr']), shape=loader['shape'])


def controversy_value(length, flags, date):
    if date == 9999:
        date = 2008
    return min(max(np.log((flags + 1) * np.sqrt(length) / np.sqrt(2018 - date)) - 4, 0), 6) / 6


def sqrt_degrees(csr_matrix):
    data = csr_matrix.data
    indptr = csr_matrix.indptr
    size = csr_matrix.shape[0]
    degrees = np.array([np.sqrt(sum(data[indptr[i]:indptr[i+1]])) for i in range(size)])
    return degrees


def weighted_adjacency_matrix(article_list, links, controversy_values):
    subset_links = {k: links.get(k, None) for k in article_list}


def grouped_controversy(article_list, links, controversy_values):
    adjacency_matrix = weighted_adjacency_matrix(article_list, links, controversy_values)


if __name__ == '__main__':
    controversy_values = {int(k): v for k, v in json.load(open(CONTROVERSY_SCORES, 'r', encoding='utf-8'), encoding='utf8').items()}
    links = json.load(open(LINKS_FILE, 'r', encoding='utf-8'), encoding='utf8')
