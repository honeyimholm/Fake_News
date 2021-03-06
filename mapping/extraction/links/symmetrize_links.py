# coding=utf8
import json
import os
from time import time
from codecs import open


from settings import DATA_FOLDER

SOURCE_FILE = os.path.join(DATA_FOLDER, 'indexed_links.json')
OUTPUT_FILE = os.path.join(DATA_FOLDER, 'symmetrized_links.json')

if __name__ == '__main__':
    start_time = time()
    indexed_links = {int(k): set(v) for k, v in json.load(open(SOURCE_FILE, 'r')).items()}
    for i, (article, citations) in enumerate(indexed_links.items()):
        for citation in citations:
            if citation in indexed_links:
                indexed_links[citation].add(article)
        if i % 10000 == 0:
            print(i)
            print(time() - start_time)

    indexed_links = {k: list(v) for k, v in indexed_links.items()}

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as g:
        json.dump(indexed_links, g, indent=2, ensure_ascii=False)