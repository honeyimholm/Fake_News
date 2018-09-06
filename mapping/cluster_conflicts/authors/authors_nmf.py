# coding=utf8
from time import time
import os
import json
from collections import Counter
import random

from settings import DATA_FOLDER, LOCAL_DATA_FOLDER, RAW_FOLDER
from sklearn.decomposition import NMF
from sklearn.preprocessing import normalize
from scipy.sparse import csr_matrix, csc_matrix
import numpy as np


TRAIN_RATIO = 0.9
AUTHORSHIP_THRESHOLD = 10
CLOSENESS_THRESHOLD = 10
EDIT_COUNT_FILE = os.path.join(DATA_FOLDER, 'edit_counts.json')


def build_matrix(edit_counts):

    train_counts_by_author = {}
    test_counts_by_author = {}
    reverse_article_index = {}

    for i, (article, counts) in enumerate(edit_counts.items()):
        reverse_article_index[article] = i
        for author, count in counts.items():
            try:
                train_counts_by_author[author][i] = count
            except KeyError:
                train_counts_by_author[author] = {i: count}

    article_index = sorted([article for article in reverse_article_index], key=lambda x: reverse_article_index[x])

    train_counts_by_author = {k: v for k, v in train_counts_by_author.items() if len(v) >= AUTHORSHIP_THRESHOLD}
    author_index = {}
    indptr = [0]
    data = []
    indices = []
    hidden_cells = []

    for i, (author, counts) in enumerate(random.sample(train_counts_by_author.items(), k=len(train_counts_by_author))):

        if i < len(train_counts_by_author) * TRAIN_RATIO:

            author_index[author] = i
            indptr.append(indptr[-1] + len(counts))
            new_indices, new_data = list(zip(*counts.items()))
            indices.extend(new_indices)
            data.extend(new_data)

        else:

            author_index[author] = i
            indptr.append(indptr[-1] + len(counts) - 1)
            new_indices, new_data = list(zip(*random.sample(counts.items(), k=len(counts))))
            indices.extend(new_indices[:-1])
            # data.extend([1 for _ in new_data[:-1]])
            data.extend(new_data[:-1])
            # data.extend(normalize_list(new_data[:-1]))
            hidden_cells.append((i, new_indices[-1], new_data[-1]))

    print('max value : {}'.format(max(data)))
    clip = np.percentile(data, 99)
    print('clipping at {}'.format(clip))
    data = [min(value, clip) for value in data]

    return csr_matrix((data, indices, indptr)), hidden_cells, article_index


def normalize_list(data_list):

    denominator = sum(data_list)

    if denominator == 0:
        return data_list
    else:
        return [data_point / denominator for data_point in data_list]


def check_decomposition(W, H, hidden_cells, article_index):

    correct_ones = 0
    hidden_rows = [cell[0] for cell in hidden_cells]
    W = W[hidden_rows, :]
    print(W.shape)
    print(H.shape)
    Y = W.dot(H)
    for i, row in enumerate(Y):
        if hidden_cells[i][1] in np.argpartition(row, -CLOSENESS_THRESHOLD)[-CLOSENESS_THRESHOLD:]:
        # if np.argmax(row) == hidden_cells[i][1]:
            correct_ones += 1
        print(article_index[np.argmax(row)], "|||||||", article_index[hidden_cells[i][1]])
    return correct_ones / float(len(hidden_cells))


if __name__ == '__main__':

    random.seed(3)

    t0 = time()
    edit_counts = json.load(open(EDIT_COUNT_FILE))
    article_author_matrix, hidden_cells, article_index = build_matrix(edit_counts)
    print('matrix shape : {}'.format(article_author_matrix.shape))
    t1 = time()
    print('matrix built in {}s'.format(t1 - t0))

    normalize(article_author_matrix, norm='l1', axis=0)
    # normalize(article_author_matrix, norm='l1', axis=1)

    # print(article_author_matrix.data)
    # article_strengths = article_author_matrix.transpose().sum(axis=1)
    # print(article_strengths)
    # print(len(article_strengths))
    # print(np.max(article_strengths) / sum(article_strengths))

    model = NMF(n_components=64, init='random', random_state=0)
    W = model.fit_transform(article_author_matrix)
    H = model.components_
    t2 = time()
    print('NMF done in {}s'.format(t2 - t1))

    print(check_decomposition(W, H, hidden_cells, article_index))