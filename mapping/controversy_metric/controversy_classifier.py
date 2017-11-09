from sklearn.ensemble import RandomForestClassifier
import json
from codecs import open
from time import time
import os

from settings import DATA_FOLDER


BAD_OUTPUT_FILE = os.path.join(DATA_FOLDER, 'bad_articles.json')
GOOD_OUTPUT_FILE = os.path.join(DATA_FOLDER, 'good_articles.json')
FINAL_INDEX_FILE = os.path.join(DATA_FOLDER, '2110_final_index.json')
TALK_DATA_FILE = os.path.join(DATA_FOLDER, '2110_talk_data.json')


if __name__ == '__main__':
    article_index = json.load(open(FINAL_INDEX_FILE, 'r', encoding='utf-8'), encoding='utf8')
    bad_articles = json.load(open(BAD_OUTPUT_FILE, 'r', encoding='utf-8'), encoding='utf8')
    good_articles = json.load(open(GOOD_OUTPUT_FILE, 'r', encoding='utf-8'), encoding='utf8')
    talk_data = json.load(open(TALK_DATA_FILE, 'r', encoding='utf-8'), encoding='utf8')

    bad_articles = [talk_data[article_index[article]] for article in bad_articles if article in article_index]

    good_articles = [talk_data[article_index[article]] for article in good_articles if article in article_index]

