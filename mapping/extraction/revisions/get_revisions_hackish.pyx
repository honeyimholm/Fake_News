# coding=utf8
import json
import os
from settings import RAW_FOLDER

DISAMBIGUATION_FILE = os.path.join(RAW_FOLDER, 'disambiguations.json')
DISAMBIGUATION_NAMES = set(json.load(open(DISAMBIGUATION_FILE, 'r', encoding='utf8'), encoding='utf8'))
PRUNED_KEYS = ['Category:', 'File:', 'Template:', 'Portal:', 'Draft:', 'MediaWiki:', 'List of', 'Wikipedia:',
               'TimedText:', 'Help:', 'Book:', 'Module:', 'Topic:']


def article_generator(file):

    with open(file, 'r') as f:

        title = None
        revisions = []
        not_article = False
        user = None
        timestamp = None
        sha1 = None


        for line in f:

            if line == '  </page>\n':
                if not not_article:
                    yield title, revisions
                title = None
                revisions = []
                not_article = False
                continue
            if not_article:
                continue

            if line[:17] == '      <timestamp>':
                timestamp = line[17:-13]
                continue

            if line[:12] == '      <sha1>':
                sha1 = line[12:-8]
                continue

            if line == '    </revision>\n':
                revisions.append((user, timestamp, sha1))
                user = None
                timestamp = None
                sha1 = None
                continue

            if line[:11] == '    <title>':
                title = line[11:-9]
                if is_to_prune(title) or "(disambiguation)" in title or title in DISAMBIGUATION_NAMES:
                    not_article = True
                continue

            if line[:8] == '    <ns>':
                if line != '    <ns>0</ns>\n':
                    not_article = True

            if line[:18] == '        <username>':
                user = line[18:-12]
                continue

            if line[:12] == '        <ip>':
                user = line[12:-6]
                continue


def is_to_prune(title):
    return any([title.startswith(key) for key in PRUNED_KEYS])