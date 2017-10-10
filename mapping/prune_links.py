# coding=utf8
import json
import os
from time import time
from codecs import open


DATA_FOLDER = '/home/teven/fake_news/Wikidumps/'
SOURCE_FILE = os.path.join(DATA_FOLDER, 'indexed_links.json')
INDEX_FILE = os.path.join(DATA_FOLDER, 'test_index.json')
REVERSE_INDEX_FILE = os.path.join(DATA_FOLDER, 'reverse_index.json')
REINDEX_FILE = os.path.join(DATA_FOLDER, 'reindex.json')
REVERSE_REINDEX_FILE = os.path.join(DATA_FOLDER, 'reverse_reindex.json')
OUTPUT_FILE = os.path.join(DATA_FOLDER, 'reindexed_pruned_links.json')


if __name__ == '__main__':
    straight_index = json.load(open(INDEX_FILE, 'r', encoding='utf8'), encoding='utf8')
    reverse_index = {v: k for k, v in straight_index.iteritems()}
    json.dump(reverse_index, open(REVERSE_INDEX_FILE, 'w', encoding='utf8'), encoding='utf8', ensure_ascii=False, indent=2)
    pruned_counter = 0
    pruned_index = {}
    reverse_pruned_index = {}
    start_time = time()
    indexed_links = json.load(open(SOURCE_FILE, 'r'))
    keys = {int(k) for k in indexed_links.keys()}
    print len(keys)
    print max(keys)
    print min(keys)
    indexed_links = {int(k): v for k, v in indexed_links.iteritems()}
    pruned_links = {article: [citation for citation in citations if article in indexed_links.get(citation, [])] for article, citations in indexed_links.iteritems()}
    for key in pruned_links.keys():
        if pruned_links[key]:
            pruned_index[key] = pruned_counter
            reverse_pruned_index[pruned_counter] = reverse_index[key]
            pruned_counter += 1
    reindexed_pruned_links = {pruned_index[article] : [pruned_index[citation] for citation in citations] for article, citations in pruned_links.iteritems() if len(citations) > 0}
    json.dump(reindexed_pruned_links, open(OUTPUT_FILE, 'w'), indent=2)
    json.dump(reverse_pruned_index, open(REVERSE_REINDEX_FILE, 'w', encoding='utf8'), encoding='utf8', ensure_ascii=False, indent=2)
    print 'links pruned in ' + str(time() - start_time)