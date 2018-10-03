import os
import json
from codecs import open

from settings import DATA_FOLDER, LANGUAGE
import datetime
from time import time

import numpy as np

from mapping.extraction.revisions.get_M import file_iterator, get_admin_reversions


SOURCE_FILE = os.path.join(DATA_FOLDER, 'revisions.txt')
ADMINSHIPS_FILE = os.path.join(DATA_FOLDER, 'admin_dates.json')
OUTPUT_FILE = os.path.join(DATA_FOLDER, 'admin_stats.json')
REDIRECT_FILE = os.path.join(DATA_FOLDER, 'redirects.json')
CONFLICT_SCORES = os.path.join(DATA_FOLDER, 'Nscores.json')

THRESHOLDS = {'EN': 99, 'FR': 95, 'DE': 95}


if __name__ == '__main__':

    scores = json.load(open(CONFLICT_SCORES))
    score_threshold = np.percentile(list(scores.values()), THRESHOLDS[LANGUAGE])
    conflicts = {article for article in scores if scores[article] > score_threshold}
    print(len(conflicts))

    adminships = json.load(open(ADMINSHIPS_FILE))
    adminships = {k: datetime.date(int(v[2]), int(v[1]), int(v[0])) for k, v in adminships.items()}
    admins_stats = {admin: {True: [0, 0, 0, 0, 0, 0], False: [0, 0, 0, 0, 0, 0]} for admin in adminships.keys()}

    redirects = json.load(open(REDIRECT_FILE, 'r'))

    total_cython_time = 0
    total_rest = 0
    articles = 0
    start_time = time()
    for i, (title, dump) in enumerate(file_iterator(SOURCE_FILE)):

        try:
            redirected_title = redirects[title]
        except KeyError:
            continue

        article_stats = get_admin_reversions(json.loads(dump), adminships)
        conflict_in_article = redirected_title in conflicts
        for admin in article_stats:
            for j in range(6):
                admins_stats[admin][conflict_in_article][j] += article_stats[admin][j]

        articles += 1

        if articles % 10000 == 0:
            print(articles)
            print(time() - start_time)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(admins_stats, f, ensure_ascii=False, indent=2)