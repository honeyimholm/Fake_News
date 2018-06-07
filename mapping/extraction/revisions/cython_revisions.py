# coding=utf8
from time import time
import os
import re
import json
from codecs import open

from settings import DATA_FOLDER, LOCAL_DATA_FOLDER, RAW_FOLDER
from src.mapping.extraction.revisions.get_revisions_hackish import article_generator

SOURCE_FILE = os.path.join(RAW_FOLDER, 'enwiki-20180520-stub-meta-history.xml')
OUTPUT_FILE = os.path.join(LOCAL_DATA_FOLDER, '0520_revisions.txt')


if __name__ == '__main__':
    article_number = 0
    start_time = time()
    with open(OUTPUT_FILE, 'w') as f:
        for i, (title, revisions) in enumerate(article_generator(SOURCE_FILE)):
            serialized = json.dumps(revisions, ensure_ascii=False)
            f.write(title + '\n')
            f.write(serialized + '\n\n')
            if i % 100000 == 0 and i > 0:
                print(i)
                print(time() - start_time)