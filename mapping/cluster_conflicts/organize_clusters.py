import os
import json
from codecs import open
from time import time


from settings import DATA_FOLDER
HIERARCHICAL_CLUSTER_FILE = os.path.join(DATA_FOLDER, 'hierarchical_clusters.json')
TITLE_TO_PATH_FILE = os.path.join(DATA_FOLDER, 'title_to_path.json')


def iterate_through_tree(nested_list, path=None):
    if path is None:
        path = tuple()
    if isinstance(nested_list, list):
        for i, sublist in enumerate(nested_list):
            subpath = path + (i,)
            for item in iterate_through_tree(sublist, subpath):
                yield item
    else:
        yield nested_list, path


if __name__ == '__main__':
    hierarchical_clusters = json.load(open(HIERARCHICAL_CLUSTER_FILE, 'r', encoding='utf8'))
    cluster_sizes = {}
    title_to_path = {}
    for item, path in iterate_through_tree(hierarchical_clusters, None):
        title_to_path[item] = path
    json.dump(title_to_path, open(TITLE_TO_PATH_FILE, 'w', encoding='utf8'), ensure_ascii=False, indent=2)