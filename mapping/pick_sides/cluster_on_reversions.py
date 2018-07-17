import requests, json
import os
from multiprocessing import Pool
import numpy as np
from collections import Counter
import scipy.sparse as sp

import networkx as nx
import community

from settings import DATA_FOLDER


if __name__ == '__main__':

    reversions = json.load(open(os.path.join(DATA_FOLDER, "0520_250_reversions.json")))
    conflicts = json.load(open(os.path.join(DATA_FOLDER, "US_political_conflicts_infomap.json")))
    reversions = {k: v for k, v in reversions.items() if k in conflicts}

    reversions = [tuple(reversion) for article in reversions.values() for reversion in article]
    total_reversions = Counter(reversions)

    comments_by_users = json.load(open(os.path.join(DATA_FOLDER, 'US_political_talk_page_comments.json'), 'r'))
    average_comment_number = np.mean([len(user_comments) for user_comments in comments_by_users.values()])
    big_users = [user for user in comments_by_users.keys() if len(comments_by_users[user]) > average_comment_number]
    users2idx = {user: i for i, user in enumerate(big_users)}

    data = [[users2idx[pair[0]], users2idx[pair[1]], -1] for pair, value in total_reversions.items() if pair[0] in users2idx and pair[1] in users2idx]\
           # + [[i, i, 1] for i in range(len(users2idx))]
    data = list(zip(*data))

    reversion_matrix = sp.csr_matrix((data[2], (data[0], data[1])), shape=(len(users2idx), len(users2idx)))
    agreement_matrix = reversion_matrix.transpose() * reversion_matrix.transpose()

    agreement_graph = nx.from_scipy_sparse_matrix(agreement_matrix, create_using=nx.Graph())
    agreement_graph = agreement_graph.to_undirected()
    clustering = community.best_partition(agreement_graph)
    print(len(set(clustering.values())))
    nx.set_node_attributes(agreement_graph, name='cluster', values=clustering)
    nx.set_node_attributes(agreement_graph, name='user', values=big_users)