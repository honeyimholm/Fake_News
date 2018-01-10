import os
import json
import scipy.sparse as sp
import numpy as npm

from settings import DATA_FOLDER

TOXICITY_FILE = os.path.join(DATA_FOLDER, 'toxicity_example.json')
CLUSTERS_FILE = os.path.join(DATA_FOLDER, '0101_conflict_clusters.json')

if __name__ == '__main__':

    toxicity = json.load(open(TOXICITY_FILE))
    clusters = json.load(open(CLUSTERS_FILE))

    for cluster in clusters:

        pass