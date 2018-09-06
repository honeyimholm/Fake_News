# coding=utf8
from time import time
import os
import json
import numpy as np

from settings import DATA_FOLDER, LOCAL_DATA_FOLDER, RAW_FOLDER
from src.mapping.extraction.revisions.get_M import file_iterator, get_M


SOURCE_FILE = os.path.join(DATA_FOLDER, 'revisions.txt')
M_FILE = os.path.join(DATA_FOLDER, 'Mscores.json')
N_FILE = os.path.join(DATA_FOLDER, 'Nscores.json')
REDIRECT_FILE = os.path.join(DATA_FOLDER, 'redirects.json')
REVERSION_FILE = os.path.join(DATA_FOLDER, 'reversions.json')
PERCENTILE = 90


def get_N(reversions, user_edit_counts):
    reversions = {tuple(reversion) for reversion in reversions}
    # reversions = {reversion for reversion in reversions if (reversion[1], reversion[0]) in reversions}
    scores = [min(user_edit_counts[reversion[0]], user_edit_counts[reversion[1]]) for reversion in reversions]
    if len(scores) > 0:
        return sum(scores) / max(sum(user_edit_counts.values()), 100) * len({reversion[0] for reversion in reversions})
    else:
        return 0


if __name__ == '__main__':
    articles = 0
    start_time = time()
    reversion_dictionary = {}
    redirects = json.load(open(REDIRECT_FILE, 'r'))
    M_scores = json.load(open(M_FILE))
    m_threshold = np.percentile([sum(score['scores']) for score in M_scores.values()], PERCENTILE)
    for i, (title, dump) in enumerate(file_iterator(SOURCE_FILE)):
        M, reversions, user_edit_counts = get_M(json.loads(dump))
        try:
            redirected_title = redirects[title]
        except KeyError:
            continue
        score = sum(M_scores.get(title, {'scores': [0]})['scores'])
        if title == "Alexander Waibel":
            print("AW = {}".format(score))
        if title == "Angela Merkel":
            print("AM = {}".format(score))
        if title == "Paris":
            print("Paris = {}".format(score))
        if title == "Karlsruhe":
            print("Karlsruhe = {}".format(score))
        if title == "Horst F. Pampel":
            print("Horst F. Pampel = {}".format(score))
        if title == "Zeit des Nationalsozialismus":
            print("Zeit des Nationalsozialismus = {}".format(score))
        if score <= m_threshold:
            continue
        try:
            reversion_dictionary[redirected_title][0].extend(reversions)
            reversion_dictionary[redirected_title][1] += user_edit_counts
        except KeyError:
            reversion_dictionary[redirected_title] = (reversions, user_edit_counts)
            articles += 1
        if articles % 1000 == 0:
            print(articles)
            print(time() - start_time)
    print(time() - start_time)
    final_scores_dictionary = {title: get_N(items[0], items[1]) for title, items in reversion_dictionary.items()}
    print(time() - start_time)
    print('dumping')
    with open(N_FILE, 'w') as g:
        json.dump(final_scores_dictionary, g, ensure_ascii=False, indent=2)
    reversion_dictionary = {title: items[0] for title, items in reversion_dictionary.items()}
    with open(REVERSION_FILE, 'w') as f:
        json.dump(reversion_dictionary, f, ensure_ascii=False, indent=2)
