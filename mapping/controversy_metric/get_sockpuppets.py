import json
import os
import requests
from time import time, sleep
import re

from settings import DATA_FOLDER


def query(request):
    request['action'] = 'query'
    request['format'] = 'json'
    retries = 0
    lastContinue = {}
    while True:
        # Clone original request
        req = request.copy()
        # Modify it with the values returned in the 'continue' section of the last result.
        req.update(lastContinue)
        # Call API
        try:
            result = requests.get('https://en.wikipedia.org/w/api.php', params=req).json()
            if 'error' in result:
                raise requests.HTTPError(result['error'])
            if 'warnings' in result:
                print(result['warnings'])
            if 'query' in result:
                yield result['query']
            if 'continue' not in result:
                break
            lastContinue = result['continue']
        except requests.exceptions.ConnectionError:
            sleep(retries * retries)
            retries += 1
            print('{} retry'.format(retries))
            continue


def remove_user_heading(page_title):
    if page_title.startswith('User:'):
        return page_title[5:]
    if page_title.startswith('User talk:'):
        return page_title[10:]


if __name__ == '__main__':

    sockpuppet_dictionary = {}

    start_time = time()

    for result in query({'list': 'categorymembers', 'cmprop': 'title', 'cmtitle': 'Category:Wikipedia sockpuppets',
                         'cmtype': 'subcat', 'cmlimit': 'max'}):

        subcategories = [item['title'] for item in result['categorymembers'] if
                         item['title'].startswith('Category:Wikipedia sockpuppets of')]

        for subcategory in subcategories:

            for result in query({'list': 'categorymembers', 'cmprop': 'title', 'cmtitle': subcategory,
                                 'cmtype': 'page', 'cmlimit': 'max'}):
                sockpuppet_dictionary[subcategory[len('Category:Wikipedia sockpuppets of '):]] = list(set(
                    remove_user_heading(item['title']) for item in result['categorymembers']))

        stop_time = time()

        print('{} done in {}'.format(len(sockpuppet_dictionary), stop_time - start_time))

    json.dump(sockpuppet_dictionary, open(os.path.join(DATA_FOLDER, 'sockpuppets_1605.json'), 'w'), ensure_ascii=False, indent=2)
