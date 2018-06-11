# coding=utf8
from time import time
import os
import json

from settings import DATA_FOLDER, LOCAL_DATA_FOLDER, RAW_FOLDER
from src.mapping.extraction.revisions.get_M import file_iterator, get_M


SOURCE_FILE = os.path.join(LOCAL_DATA_FOLDER, '0520_revisions.txt')
OUTPUT_FILE = os.path.join(DATA_FOLDER, '0520_Mscores.txt')
REDIRECT_FILE = os.path.join(DATA_FOLDER, 'redirects.json')


if __name__ == '__main__':
    articles = 0
    start_time = time()
    reversion_dictionary = {}
    redirects = json.load(open(REDIRECT_FILE, 'r'))
    for i, (title, dump) in enumerate(file_iterator(SOURCE_FILE)):
        M, reversions, _ = get_M(json.loads(dump))
        try:
            redirected_title = redirects[title]
        except KeyError:
            continue
        try:
            reversion_dictionary[redirected_title].append(M)
        except KeyError:
            reversion_dictionary[redirected_title] = [M]
            articles += 1
        # if articles == 30000:
        #     print(time() - start_time)
        #     break
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(reversion_dictionary, f, ensure_ascii=False, indent=2)