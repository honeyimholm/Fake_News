import os
import json
from codecs import open
from time import time
from settings import API_KEY, DATA_FOLDER, RAW_FOLDER

from mapping.infomap import infomap


LINKS_FILE = os.path.join(DATA_FOLDER, 'symmetrized_links.json')
FINAL_INDEX_FILE = os.path.join(DATA_FOLDER, 'final_index.json')
REVERSE_INDEX_FILE = os.path.join(DATA_FOLDER, 'reverse_index.json')
CONFLICT_SCORES = os.path.join(DATA_FOLDER, 'Nscores.json')
HIERARCHICAL_CLUSTER_FILE = os.path.join(DATA_FOLDER, 'hierarchical_clusters.json')


def time_step(current_time):
    print(str(time() - current_time) + 's elapsed')
    return time()


def total_elements(nested_list):
    if isinstance(nested_list, list):
        return sum([total_elements(item) for item in nested_list])
    else:
        return 1


def recursive_sort(nested_list):
    if isinstance(nested_list, list):
        nested_list.sort(key=total_elements, reverse=True)
        for item in nested_list:
            recursive_sort(item)
    else:
        return None


if __name__ == '__main__':

    t_start = time()

    scores = json.load(open(CONFLICT_SCORES))
    wars = sorted([k for k in scores], key=lambda x: scores[x], reverse=True)

    print(len(wars))
    print('done')
    index = json.load(open(FINAL_INDEX_FILE))
    index = {k: index[k] for k in wars if k in index}
    print(len(index))
    print('done')
    wars = [index[item] for item in wars if item in index]
    filter_index = {k: i for i, k in enumerate(wars)}
    print(len(wars))
    print('done')
    wars_links = json.load(open(LINKS_FILE))
    print('done')
    wars_links = {war: wars_links[str(war)] for war in wars if str(war) in wars_links}
    print(len(wars_links))
    print('done')
    wars_links = {k: v for k, v in wars_links.items()}
    print(len(wars_links))
    print('done')
    reverse_index = {filter_index[v]: k for k, v in index.items()}
    print('done')

    clusterer = infomap.Infomap(
        str("--directed --zero-based-numbering  --tune-iteration-threshold  1e-5 --markov-time 0.8"))
    indexed_citations = wars_links
    for article, citations in indexed_citations.items():
        if article in filter_index:
            for citation in citations:
                if citation in filter_index:
                    clusterer.addLink(filter_index[int(article)], filter_index[citation])
    print('network built')
    clusterer.run()
    tree = clusterer.tree
    print('clusters built')
    current_time = time_step(t_start)

    hierarchical_clusters = []
    t0 = time()
    current_upper_cluster = 0
    missing = 0
    for i, node in enumerate(tree.treeIter()):
        if node.isLeaf:
            current_list = hierarchical_clusters
            for index in node.path()[:-1]:
                try:
                    current_list = current_list[index]
                except IndexError:
                    current_list.append([])
                    current_list = current_list[-1]
            try:
                title = reverse_index[int(node.data.name)]
                current_list.append({'title': title, 'score': scores[title]})
                if title == "Alexander Waibel":
                    print("AW = {}".format(scores[title]))
                if title == "Angela Merkel":
                    print("AM = {}".format(scores[title]))
                if title == "Paris":
                    print("Paris = {}".format(scores[title]))
                if title == "Karlsruhe":
                    print("Karlsruhe = {}".format(scores[title]))
                if title == "Horst F. Pampel":
                    print("Horst F. Pampel = {}".format(scores[title]))
                if title == "Zeit des Nationalsozialismus":
                    print("Zeit des Nationalsozialismus = {}".format(scores[title]))
            except KeyError:
                missing += 1
                print(node.data.name)
                print(len(reverse_index.keys()))
                print()
            if node.path()[0] != current_upper_cluster:
                current_upper_cluster = node.path()[0]

    print(total_elements(hierarchical_clusters))
    recursive_sort(hierarchical_clusters)
    # print(hierarchical_clusters)

    json.dump(hierarchical_clusters, open(HIERARCHICAL_CLUSTER_FILE, 'w'), indent=2)
    print('clusters dumped')
    current_time = time_step(t_start)