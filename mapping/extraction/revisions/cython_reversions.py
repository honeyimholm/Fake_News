# coding=utf8
from time import time
import os
import json

from settings import DATA_FOLDER, LOCAL_DATA_FOLDER, RAW_FOLDER
from src.mapping.extraction.revisions.get_M import file_iterator, get_M


SOURCE_FILE = os.path.join(LOCAL_DATA_FOLDER, '0520_revisions.txt')
M_FILE = os.path.join(DATA_FOLDER, '0520_Mscores.txt')
REDIRECT_FILE = os.path.join(DATA_FOLDER, 'redirects.json')
OUTPUT_FILE = os.path.join(DATA_FOLDER, '0520_500_reversions.txt.json')
M_THRESHOLD = 500   ²A  


if __name__ == '__main__':
    articles = 0
    start_time = time()
    reversion_dictionary = {}
    redirects = json.load(open(REDIRECT_FILE, 'r'))
    M_scores = json.load(open(M_FILE))
    for i, (title, dump) in enumerate(file_iterator(SOURCE_FILE)):
        M, reversions = get_M(json.loads(dump))
        try:
            redirected_title = redirects[title]
        except KeyError:
            continue
        if sum(M_scores.get(title, [])) < M_THRESHOLD:
            continue
        try:
            reversion_dictionary[redirected_title].extend(reversions)
        except KeyError:
            reversion_dictionary[redirected_title] = reversions
            articles += 1
        # if articles == 1000:
        #     print(time() - start_time)
        #     break
    print(time() - start_time)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(reversion_dictionary, f, ensure_ascii=False, indent=2)