import json
import os
from time import time

from util_wikiapi import get_revisions_from_title
from settings import DATA_FOLDER


clusters = json.load(open(os.path.join(DATA_FOLDER, 'final_clusters_0218.json')))

print(len(clusters[3]))
revisions = {title: get_revisions_from_title(title, 5000) for title in clusters[3]}

json.dump(revisions, open(os.path.join(DATA_FOLDER, 'balkan_revisions.json'), 'w'), ensure_ascii=False, indent=2)