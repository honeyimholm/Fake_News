# coding=utf8
from collections import Counter


def file_iterator(file):
    current_article = None
    with open(file, 'r') as f:
        for i, line in enumerate(f):
            if i % 3 == 0:
                current_article = line[:-1]
            if i % 3 == 1:
                yield current_article, line[:-1]


def get_M(article_revisions):

    M = 0
    user_edit_counts = Counter([revision[0] for revision in article_revisions])
    sha1_dict = {}
    reversions = []
    next_user = None

    for revision in reversed(article_revisions):

        try:
            user_pair = (revision[0], sha1_dict[revision[2]])
            reversions.append(user_pair)
            M += min(user_edit_counts[user_pair[0]], user_edit_counts[user_pair[1]])
        except KeyError:
            pass

        sha1_dict[revision[2]] = next_user
        next_user = revision[0]

    # print(sha1_dict)

    return M, reversions
