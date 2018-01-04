import requests
import os
import json
from codecs import open
from time import time

from bs4 import BeautifulSoup

from .get_talks import clean_talk_title
from settings import DATA_FOLDER


BAD_OUTPUT_FILE = os.path.join(DATA_FOLDER, 'bad_articles.json')
GOOD_OUTPUT_FILE = os.path.join(DATA_FOLDER, 'good_articles.json')
FEATURED_DICT = os.path.join(DATA_FOLDER, 'featured_dict.json')
FINAL_INDEX_FILE = os.path.join(DATA_FOLDER, '2110_final_index.json')
TALK_DATA_FILE = os.path.join(DATA_FOLDER, '2110_talk_data.json')


def is_page_link(tag):
    return tag.name == 'li' and tag.a


def is_good_article(tag):
    return tag.name == 'p' and tag.a


def handle_page(url, counter, article_names):
    r = requests.get(url)
    r.encoding = 'utf8'
    source = r.text
    soup = BeautifulSoup(source, 'lxml')
    if counter == 0:
        bad_articles = [clean_talk_title(tag.a.string, article_names) for i, tag in enumerate(soup.find_all(is_page_link)[12:-49])]
    else:
        bad_articles = [clean_talk_title(tag.a.string, article_names) for i, tag in enumerate(soup.find_all(is_page_link)[10:-49])]
    try:
        next_page_tag = soup.find_all("a", string="next page")[0]
        next_page_url = 'https://en.wikipedia.org' + next_page_tag['href']
    except IndexError:
        next_page_url = None
    return bad_articles, next_page_url


def handle_featured(url, upper_bound, lower_bound):
    r = requests.get(url)
    r.encoding = 'utf8'
    source = r.text
    soup = BeautifulSoup(source, 'lxml')
    good_articles = [tag.a['title'] for i, tag in
                    enumerate(soup.find_all(is_page_link)[upper_bound:lower_bound])]
    return good_articles


def handle_good(url, upper_bound, lower_bound):
    r = requests.get(url)
    r.encoding = 'utf8'
    source = r.text
    soup = BeautifulSoup(source, 'lxml')
    good_articles = []
    categories = [tag.find_all('a') for i, tag in
                    enumerate(soup.find_all(is_good_article)[23:])]
    for i, category in enumerate(categories):
        articles = [tag['title'] for tag in category if 'title' in tag.attrs]
        good_articles.extend(articles)
    return good_articles


if __name__ == '__main__':
    article_index = json.load(open(FINAL_INDEX_FILE, 'r', encoding='utf-8'), encoding='utf8')
    article_names = set(article_index.keys())

    bad_titles = list()
    next_page_url = 'https://en.wikipedia.org/wiki/Category:Wikipedia_controversial_topics'
    counter = 0

    while next_page_url is not None:
        bad_articles, next_page_url = handle_page(next_page_url, counter, article_names)
        bad_titles.extend(bad_articles)
        counter += 1

    with open(BAD_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(bad_titles, f, encoding='utf8', ensure_ascii=False, indent=2)

    url = 'https://en.wikipedia.org/wiki/Wikipedia:Featured_articles'
    featured_titles = handle_featured(url, 53, -215)

    featured_dict = [(article, 0) for article in featured_titles]

    url = 'https://en.wikipedia.org/wiki/Wikipedia:Good_articles/all'
    good_titles = handle_good(url, 53, -215)

    good_titles.extend(featured_titles)

    with open(GOOD_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(good_titles, f, encoding='utf8', ensure_ascii=False, indent=2)

    with open(FEATURED_DICT, 'w', encoding='utf-8') as f:
        json.dump(featured_dict, f, encoding='utf8', ensure_ascii=False, indent=2)
