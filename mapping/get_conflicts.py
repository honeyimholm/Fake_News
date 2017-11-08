# coding=utf8

import time
import os
import re
import json
from codecs import open
import scipy.sparse as sp
import numpy as np

from group_controversy import controversy_value


from settings import DATA_FOLDER
RAW_FOLDER = '/home/teven/fake_news/Wikidumps/raw/'
REVERSE_INDEX_FILE = os.path.join(DATA_FOLDER, '2110_reverse_index.json')
TALK_DATA_FILE = os.path.join(DATA_FOLDER, '2110_talk_data.json')
LINKS_FILE = os.path.join(DATA_FOLDER, '2110_symmetrized_links.json')
ADJACENCY_MATRIX = os.path.join(DATA_FOLDER, '2110_conflict_adjacency.txt')
MATRIX_INDEX = os.path.join(DATA_FOLDER, '2110_conflict_matrix_index.txt')
CONTROVERSY_SCORES = os.path.join(DATA_FOLDER, '2110_controversy_scores.txt')


def save_sparse_csr(filename, data, indices, indptr, shape):
    np.savez(filename, data=data, indices=indices,
             indptr=indptr, shape=shape)




if __name__ == '__main__':

    talk_data = json.load(open(TALK_DATA_FILE, 'r', encoding='utf-8'), encoding='utf8')
    controversial_articles = {article: controversy_value(*values) for article, values in talk_data.iteritems() if controversy_value(*values) > 0}

    with open(CONTROVERSY_SCORES, 'w', encoding='utf-8') as g:
        json.dump(controversial_articles, g, encoding='utf8', indent=2, ensure_ascii=False)

    controversial_articles = {int(k): v for k, v in controversial_articles.iteritems() if v > 0.15}
    print str(len(controversial_articles)) + " controversial articles"

    print "talk data loaded"

    links = {int(k): v for k, v in json.load(open(LINKS_FILE, 'r', encoding='utf-8'), encoding='utf8').iteritems()}
    controversial_links = {article: citations for article, citations in links.iteritems() if int(article) in controversial_articles}

    print "links extracted"

    reverse_index = json.load(open(REVERSE_INDEX_FILE, 'r', encoding='utf-8'), encoding='utf8')

    reverse_controversial_index = {article: reverse_index[article] for article in controversial_articles.keys() if article in reverse_index}
    matrix_index = []

    print "indexes built"

    indptr = [0]
    data = []
    indices = []

    current_pointer = 0

    for i, (article, citations) in enumerate(controversial_links.iteritems()):
        if len(citations) > 0:
            matrix_index.append(article)
            current_pointer += len(citations) + 1
            indptr.append(current_pointer)
            data.extend([1/np.sqrt(len(citations))] * len(citations))
            data.append(np.sqrt(len(citations)))
            indices.extend(citations)
            indices.append(i)

    with open(MATRIX_INDEX, 'w', encoding='utf-8') as g:
        json.dump(matrix_index, g, encoding='utf8', indent=2, ensure_ascii=False)

    print "matrix arrays created"

    print len(data)
    controversy_matrix = sp.csc_matrix((data, indices, indptr))
    print controversy_matrix.shape

    print "matrix created"

    controversial_adjacency = controversy_matrix.transpose() * controversy_matrix
    shape = controversial_adjacency.shape
    data = controversial_adjacency.data
    indices = controversial_adjacency.indices
    indptr = controversial_adjacency.indptr

    print "adjacency matrix created"

    save_sparse_csr(ADJACENCY_MATRIX, data, indices, indptr, shape)

    print "adjacency matrix dumped"