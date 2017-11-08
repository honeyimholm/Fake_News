import requests
import os
import json
from codecs import open
from time import time

from bs4 import BeautifulSoup

from settings import DATA_FOLDER
OUTPUT_FILE = os.path.join(DATA_FOLDER, 'disambiguations.json')


def is_page_link(tag):
    return tag.name == 'li' and tag.a


def handle_page(url):
    r = requests.get(url)
    r.encoding = 'utf8'
    source = r.text
    soup = BeautifulSoup(source, 'lxml')
    disambiguations = [tag.a.string for i, tag in enumerate(soup.find_all(is_page_link, limit=203)) if i > 2]
    try:
        next_page_tag = soup.find_all("a", string="next page")[0]
        next_page_url = 'https://en.wikipedia.org' + next_page_tag['href']
    except IndexError:
        next_page_url = None
    return disambiguations, next_page_url


if __name__ == '__main__':
    start_time = time()
    disambiguation_titles = list()
    next_page_url = 'https://en.wikipedia.org/w/index.php?title=Category:All_article_disambiguation_pages&pageuntil=1st+New+Brunswick+general+election#mw-pages'
    counter = 0
    while next_page_url is not None:
        disambiguations, next_page_url = handle_page(next_page_url)
        disambiguation_titles.extend(disambiguations)
        if counter % 10 == 0:
            print counter
            print time() - start_time
        counter += 1
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(disambiguation_titles, f, encoding='utf8', ensure_ascii=False, indent=2)