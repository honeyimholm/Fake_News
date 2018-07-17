import requests
import os
import json
from codecs import open
from time import time

from settings import LANGUAGE, DATA_FOLDER
from mapping.controversy_metric.get_sockpuppets import query

OUTPUT_FILE = os.path.join(DATA_FOLDER, 'disambiguations.json')

if LANGUAGE == "EN":
    api_address = 'https://en.wikipedia.org/w/api.php'
    category = 'Category:Wikipedia sockpuppets'
if LANGUAGE == "FR":
    api_address = 'https://fr.wikipedia.org/w/api.php'
    category = 'Catégorie:Homonymie'
if LANGUAGE == "DE":
    api_address = 'https://de.wikipedia.org/w/api.php'
    category = 'Kategorie:Begriffsklärung'


if __name__ == '__main__':

    start_time = time()
    disambiguation_titles = list()

    for result in query({'list': 'categorymembers', 'cmprop': 'title', 'cmtitle': category,
                         'cmtype': 'page', 'cmlimit': 'max'}, api_address):

        print(result)

        for page in result['categorymembers']:

            disambiguation_titles.append(page['title'])

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(disambiguation_titles, f, ensure_ascii=False, indent=2)
