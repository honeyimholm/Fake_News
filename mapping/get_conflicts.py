# coding=utf8

import time
import os
import re
import json
from codecs import open

DATA_FOLDER = '/home/teven/fake_news/Wikidumps/'
RAW_FOLDER = '/home/teven/fake_news/Wikidumps/raw/'
FINAL_INDEX_FILE = os.path.join(DATA_FOLDER, '2110_final_index.json')
TALK_DATA_FILE = os.path.join(DATA_FOLDER, '2110_talk_data.json')

talk_data = json.load(open(TALK_DATA_FILE, 'r', encoding='utf-8'), encoding='utf8')

