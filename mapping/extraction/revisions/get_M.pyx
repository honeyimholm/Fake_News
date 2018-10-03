# coding=utf8
import datetime
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
            user_pair = (next_user, sha1_dict[revision[2]])
            if user_pair[0] != user_pair[1]:
                reversions.append(user_pair)
                M += min(user_edit_counts[user_pair[0]], user_edit_counts[user_pair[1]])
        except KeyError:
            pass

        sha1_dict[revision[2]] = revision[0]
        next_user = revision[0]

    return M, reversions, user_edit_counts


def get_N_enwiki(article_revisions):

    M = 0
    user_edit_counts = Counter([revision[0] for revision in article_revisions])
    sha1_dict = {}
    reversions = []
    next_user = None

    for revision in reversed(article_revisions):

        try:
            user_pair = (next_user, sha1_dict[revision[2]])
            if user_pair[0] != user_pair[1]:
                reversions.append(user_pair)
                M += min(user_edit_counts[user_pair[0]], user_edit_counts[user_pair[1]])
        except KeyError:
            pass

        sha1_dict[revision[2]] = revision[0]
        next_user = revision[0]

    N = M / max(sum(user_edit_counts.values()), 100) * len({reversion[0] for reversion in reversions})

    return N


def get_admin_reversions(article_revisions, admin_dict):

    admins = admin_dict.keys()
    article_users =  {revision[0] for revision in article_revisions}
    if article_users.isdisjoint(admins):
        return {}
    else:
        article_admins = article_users.intersection(admins)
        admin_edits = {admin: [0, 0, 0, 0, 0, 0] for admin in article_admins}

    sha1_dict = {}
    next_user = None
    # user_edit_counts = Counter([revision[0] for revision in article_revisions])


    for revision in reversed(article_revisions):

        try:

            before = admin_before_timestamp(admin_dict[revision[0]], revision[1])
            if before:
                admin_edits[revision[0]][0] += 1
            else:
                admin_edits[revision[0]][3] += 1

            try:
                user_pair = (next_user, sha1_dict[revision[2]])
                if user_pair[0] != user_pair[1]:
                    if user_pair[0] in article_admins:
                        if before:
                            admin_edits[revision[0]][1] += 1
                        else:
                            admin_edits[revision[0]][4] += 1
                    if user_pair[1] in article_admins:
                        if before:
                            admin_edits[revision[0]][2] += 1
                        else:
                            admin_edits[revision[0]][5] += 1

            except KeyError:
                    pass

        except KeyError:
            pass



        sha1_dict[revision[2]] = revision[0]
        next_user = revision[0]

    return admin_edits


def admin_before_timestamp(admin_date, article_timestamp):
    article_timestamp = datetime.datetime.strptime(article_timestamp, '%Y-%m-%dT%H:%M:%SZ').date()
    if admin_date < article_timestamp:
        return True
    else:
        return False

