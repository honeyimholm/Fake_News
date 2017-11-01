# coding=utf8
import json
import os
from time import time
from codecs import open
from string import capwords
import numpy as np

DATA_FOLDER = '/home/teven/fake_news/Wikidumps/'
SOURCE_FILE = os.path.join(DATA_FOLDER, '2110_links.txt')
INDEX_FILE = os.path.join(DATA_FOLDER, '2110_index.json')
OUTPUT_FILE = os.path.join(DATA_FOLDER, '2110_indexed_links.json')

if __name__ == '__main__':
    start = time()
    article_index = json.load(open(INDEX_FILE, 'r', encoding='utf-8'), encoding='utf8')
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        bad_article = False
        main_id = None
        main_title = None
        article_links = []
        links_dict = {}
        article_number = 0
        for line in f:
            if line == "\n":
                if main_id is not None:
                    links_dict[main_id] = article_links
                bad_article = False
                main_id = None
                article_links = []
                article_number += 1
                if article_number % 10000 == 0:
                    print str(article_number) + " articles"
                    print str(time() - start) + "s"
                continue
            if bad_article:
                continue
            title = line[0:-1]
            new_id = article_index.get(title, None)
            if new_id is None:
                new_id = article_index.get(capwords(title), None)
            if main_id is None:
                if new_id is None:
                    bad_article = True
                    print title
                    print capwords(title)
                    print new_id
                    print
                else:
                    main_id = new_id
            else:
                if new_id:
                    article_links.append(new_id)
    print "average number of links : " + str(np.mean([len(links) for links in links_dict.values()]))
    print "total number of indices : " + str(len({item for sublist in links_dict.values() for item in sublist} | set(links_dict.keys())))
    print "max index: " + str(max({item for sublist in links_dict.values() for item in sublist} | set(links_dict.keys())))
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as g:
        json.dump(links_dict, g, encoding='utf8', indent=2, ensure_ascii=False)