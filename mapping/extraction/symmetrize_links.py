# coding=utf8
import json
import os
from time import time
from codecs import open


from settings import DATA_FOLDER
SOURCE_FILE = os.path.join(DATA_FOLDER, '2110_indexed_links.json')
OUTPUT_FILE = os.path.join(DATA_FOLDER, '2110_symmetrized_links.json')

if __name__ == '__main__':
    start_time = time()
    indexed_links = {int(k): set(v) for k, v in json.load(open(SOURCE_FILE, 'r')).iteritems()}
    for i, (article, citations) in enumerate(indexed_links.iteritems()):
        for citation in citations:
            if citation in indexed_links:
                indexed_links[citation].add(article)
        if i % 10000 == 0:
            print i
            print time() - start_time

    indexed_links = {k: list(v) for k, v in indexed_links.iteritems()}

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as g:
        json.dump(indexed_links, g, encoding='utf8', indent=2, ensure_ascii=False)