# coding=utf8
from time import time
import os
import json

from settings import DATA_FOLDER, LOCAL_DATA_FOLDER, RAW_FOLDER
from src.mapping.extraction.revisions.get_M import file_iterator, get_M


SOURCE_FILE = os.path.join(LOCAL_DATA_FOLDER, '0520_revisions.txt')
M_FILE = os.path.join(DATA_FOLDER, '0520_Mscores.json')
FINAL_M_FILE = os.path.join(DATA_FOLDER, '0520_finalMscores.json')
REDIRECT_FILE = os.path.join(DATA_FOLDER, 'redirects.json')
OUTPUT_FILE = os.path.join(DATA_FOLDER, '0520_500_reversions.json')
M_THRESHOLD = 250


def get_final_M(reversions, user_edit_counts):
    reversions = {tuple(reversion) for reversion in reversions}
    reversions = {reversion for reversion in reversions if (reversion[1], reversion[0]) in reversions}
    scores = [min(user_edit_counts[reversion[0]], user_edit_counts[reversion[1]]) for reversion in reversions]
    if len(scores) > 0:
        return sum(scores) - max(scores)
    else:
        return 0


if __name__ == '__main__':
    articles = 0
    start_time = time()
    reversion_dictionary = {}
    redirects = json.load(open(REDIRECT_FILE, 'r'))
    M_scores = json.load(open(M_FILE))
    for i, (title, dump) in enumerate(file_iterator(SOURCE_FILE)):
        M, reversions, user_edit_counts = get_M(json.loads(dump))
        try:
            redirected_title = redirects[title]
        except KeyError:
            continue
        if sum(M_scores.get(title, [])) < M_THRESHOLD:
            continue
        try:
            reversion_dictionary[redirected_title][0].extend(reversions)
            reversion_dictionary[redirected_title][1] += user_edit_counts
        except KeyError:
            reversion_dictionary[redirected_title] = (reversions, user_edit_counts)
            articles += 1

    print(time() - start_time)
    final_scores_dictionary = {title: get_final_M(items[0], items[1]) for title, items in reversion_dictionary.items()}
    print(time() - start_time)
    with open(FINAL_M_FILE, 'w') as g:
        json.dump(final_scores_dictionary, g, ensure_ascii=False, indent=2)
    reversion_dictionary = {title: items[0] for title, items in reversion_dictionary.items()}
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(reversion_dictionary, f, ensure_ascii=False, indent=2)
