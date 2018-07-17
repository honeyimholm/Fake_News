# coding=utf8
from time import time
import os
import json
from collections import Counter

from settings import DATA_FOLDER, LOCAL_DATA_FOLDER, RAW_FOLDER
from mapping.extraction.revisions.src.mapping.extraction.revisions.get_M import file_iterator


SOURCE_FILE = os.path.join(DATA_FOLDER, 'revisions.txt')
N_FILE = os.path.join(DATA_FOLDER, 'Nscores.json')
AUTHOR_FILE = os.path.join(DATA_FOLDER, 'edit_counts.json')
REDIRECT_FILE = os.path.join(DATA_FOLDER, 'redirects.json')


if __name__ == '__main__':
    articles = 0
    start_time = time()
    count_dictionary = {}
    N_scores = json.load(open(N_FILE, 'r'))
    redirects = json.load(open(REDIRECT_FILE, 'r'))
    for i, (title, dump) in enumerate(file_iterator(SOURCE_FILE)):
        try:
            redirected_title = redirects[title]
        except KeyError:
            continue
        if redirected_title not in N_scores:
            continue
        article_revisions = json.loads(dump)
        edit_counts = Counter([revision[0] for revision in article_revisions])
        count_dictionary[redirected_title] = dict(edit_counts)
        articles += 1
        if articles == 30000:
            print(time() - start_time)
    with open(AUTHOR_FILE, 'w') as f:
        json.dump(count_dictionary, f, ensure_ascii=False, indent=2)
