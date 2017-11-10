import requests
import os
import json
from codecs import open
import re
from time import time
import urllib
from collections import Counter

from bs4 import BeautifulSoup

from settings import DATA_FOLDER


FINAL_INDEX_FILE = os.path.join(DATA_FOLDER, '2110_final_index.json')
OUTPUT_FILE = os.path.join(DATA_FOLDER, 'edit_wars.json')

HEADER_REGEX = re.compile("==+[^\n]*==+")
ARTICLE_REGEX = re.compile("{{(?:[Aa]rticle|pagelinks)\|.*?}}")


def handle_url(url):
    r = requests.get(url)
    r.encoding = 'utf8'
    source = r.text
    soup = BeautifulSoup(source, 'lxml')
    text = soup.textarea.string
    text = re.sub(HEADER_REGEX, "#SEPARATOR#SEPARATOR#", text)
    chunks = text.split("#SEPARATOR#SEPARATOR#")[1:]
    articles = [extract_article(re.search(ARTICLE_REGEX, chunk)) for chunk in chunks if re.search(ARTICLE_REGEX, chunk)]
    return articles


def extract_article(regex_result):
    if regex_result is None:
        return None
    else:
        text = regex_result.group()
    initial_pos = text.find("|")
    text = urllib.unquote(text[initial_pos + 1:-2])
    if '_' in text:
        text = text.replace("_", " ")
    return text


if __name__ == '__main__':
    article_index = json.load(open(FINAL_INDEX_FILE, 'r', encoding='utf-8'), encoding='utf8')
    article_names = set(article_index.keys())

    bad_titles = list()
    base_url = "https://en.wikipedia.org/w/index.php?title=Wikipedia:Administrators'_noticeboard/3RRArchive"
    counter = 0

    wars = []
    for archive_number in range(1, 355):
        url = base_url + str(archive_number) + "&action=edit"
        articles = [article for article in handle_url(url) if article in article_names]
        wars.extend(articles)
        print archive_number

    wars = dict(Counter(wars))
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(wars, f, encoding='utf8', ensure_ascii=False, indent=2)