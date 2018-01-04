# coding=utf8
import xml.etree.ElementTree as etree
import time
import os
import re
import json
import string
import numpy as np
from multiprocessing import Pool
from codecs import open

from settings import DATA_FOLDER


RAW_FOLDER = '/home/teven/fake_news/Wikidumps/raw/'
SOURCE_FILE = os.path.join(RAW_FOLDER, 'enwiki-20170820-pages-meta-current.xml')
DISAMBIGUATION_FILE = os.path.join(RAW_FOLDER, 'disambiguations.json')
FINAL_INDEX_FILE = os.path.join(DATA_FOLDER, '2110_final_index.json')
TALK_DATA_FILE = os.path.join(DATA_FOLDER, '2110_talk_data.json')

ARCHIVE_PATTERN = re.compile("(?:/[Aa]rchive|/old)[ a-z0-9]*$")

DATE_PATTERN = re.compile("\[\[(?:Special:Contributions|User:).*?\|.*?\]\](?:\s*\(\[\[User talk\:.*?\|talk\]\]\)|)[A-Za-z0-9 ,:]*?20[0-1][0-9]")

DISAMBIGUATION_NAMES = set(json.load(open(DISAMBIGUATION_FILE, 'r', encoding='utf8'), encoding='utf8'))

ACRONYM_FLAGS = ['OR', 'POV', 'DUE', 'UNDUE', 'IDHT', 'NPA', 'PA', 'IDLI', 'DFT', 'DFTT', 'ANI', 'TE', 'DENY', 'SPI',
                 '3RR', '1RR', '3RRNO', 'BLP', 'BRD', 'DUCK', 'FOC', 'INDEF', 'CONSENSUS', 'NOCON', 'FORUMSHOP', 'SYN',
                 'OWNTP', 'AOHA', 'HAR', 'HARASS', 'RELEVANT', 'IJUSTDONTLIKEIT', 'CHERRY']

PRUNED_KEYS = ['Category:', 'File:', 'Template:', 'Portal:', 'Draft:', 'MediaWiki:', 'List of', 'Wikipedia:', 'TimedText:',
               'Help:', 'Book:', 'Module:', 'Topic:']

USER_REGEX = re.compile("\[\[(?:User|Special:Contributions|User talk:)[^#<>[\]|{}/@]*?[|, /]")

COLON_REGEX = re.compile("[:*]+")

FLAG_LENGTHS = [len(flag) for flag in ACRONYM_FLAGS]

PAGE_TAGS = ['{{recruiting}}', '{{controversial}}', '{{calm}}']

NOT_TEXT_REGEX = re.compile("(?:\(+.*?\)+|\[+.*?\]+|{+.*?}+|==+.*?==+)")

printable = set(string.printable)
article_index = json.load(open(FINAL_INDEX_FILE, 'r', encoding='utf-8'), encoding='utf8')
article_names = set(article_index.keys())

def strip_tag_name(t):
    t = t.split('}')[1]
    return t


def article_generator(file):

    title = None
    text = None
    do_not_parse = False

    with open(file) as xml_file:
        generator = etree.iterparse(xml_file, events=('start', 'end'))
        _, root = next(generator)

        for event, elem in generator:
            xml_tag = strip_tag_name(elem.tag)

            if event == 'start':
                if xml_tag == 'page':
                    title = None
                    text = None
                    do_not_parse = False

            else:
                if do_not_parse:
                    continue
                if xml_tag == 'title':
                    title = elem.text
                    if not title.startswith("Talk:"):
                        do_not_parse = True
                    title = clean_talk_title(title, article_names)
                    if is_to_prune(title) or "(disambiguation)" in title or title in DISAMBIGUATION_NAMES:
                        do_not_parse = True
                if xml_tag == 'text':
                    text = elem.text
                if xml_tag == 'ns':
                    if elem.text not in ['1']:
                        do_not_parse = True
                if xml_tag == 'page':
                    if title and text:
                        yield [title, text]
                    root.clear()


def last_forward_slash(title):
    index = len(title)
    for i, char in enumerate(reversed(title)):
        if char == "/":
            index = index - i - 1
    return index


def clean_talk_title(title, article_names):
    if title.startswith("Talk:"):
        title = title[5:]
    archive_match = re.search(ARCHIVE_PATTERN, title)
    if archive_match:
        title = title[0:archive_match.start()]
    if "/" in title:
        if title in article_names:
            return title
        else:
            return clean_talk_title(title[0:last_forward_slash(title)], article_names)
    else:
        return title


def is_to_prune(title):
    return any([title.startswith(key) for key in PRUNED_KEYS])


def clean_user_tag(user):
    user = user[2:-1]
    for tag in ["User talk:", "User:", "Special:Contributions/"]:
        if user.startswith(tag):
            return user[len(tag):]
    else:
        return None


def clean_text(text):
    cleaner = re.sub(NOT_TEXT_REGEX, "", text)
    if cleaner == text:
        return cleaner
    else:
        return clean_text(cleaner)


def analyze_text(text):

    flag_count = 0
    length = len(text)

    colons = re.findall(COLON_REGEX, text)
    colons.append(":")
    max_answer = max([len(colon_sequence) for colon_sequence in colons])

    users = re.findall(USER_REGEX, text)
    users = {clean_user_tag(user) for user in users if clean_user_tag(user) is not None}

    tags = set()
    for tag in PAGE_TAGS:
        if tag in text:
            tags.add(tag)
    for i in range(length):
        if text[i:i+3].upper() == 'WP:':
            if any([text[i+3:i+3+j].upper() in ACRONYM_FLAGS for j in FLAG_LENGTHS]):
                flag_count += 1

    return length, flag_count, max_answer, users, tags


def handle_article(article):

    title, text = article[0], article[1]

    article_id = article_index.get(title, None)
    dates = [int(match[-4:]) for match in re.findall(DATE_PATTERN, text)]
    dates.append(9999)
    date = min(dates)

    flag_count = 0
    length = len(text)

    colons = re.findall(COLON_REGEX, text)
    colons.append(":")
    max_answer = max([len(colon_sequence) for colon_sequence in colons])

    users = re.findall(USER_REGEX, text)
    users = {clean_user_tag(user) for user in users if clean_user_tag(user) is not None}

    tags = set()
    for tag in PAGE_TAGS:
        if tag in text:
            tags.add(tag)
    for i in range(length):
        if text[i:i+3].upper() == 'WP:':
            if any([text[i+3:i+3+j].upper() in ACRONYM_FLAGS for j in FLAG_LENGTHS]):
                flag_count += 1


    return article_id, length, flag_count, date, max_answer, users, tags


if __name__ == '__main__':
    pool = Pool(4)
    problems = 0
    talk_data = {article_id: [] for article_id in list(article_index.values())}

    print('starting')
    start_time = time.time()
    for i, (article_id, length, flag_count, date, max_answer, users, tags) in enumerate(pool.imap_unordered(handle_article, article_generator(SOURCE_FILE))):
        if i == 0:
            print(i)
            print(time.time() - start_time)
        if article_id is None:
            problems += 1
            continue
        else:
            talk_data[article_id].append((length, flag_count, date, max_answer, users, tags))
        if i % 10000 == 0:
            print(str(i - problems) + "/" + str(i))
            print(str(time.time() - start_time) + "s")
    talk_data = {article_id: (
                              sum([data[0] for data in values]),
                              sum([data[1] for data in values]),
                              min([data[2] for data in values]),
                              max([data[3] for data in values]),
                              len(set.union(*[data[4] for data in values])),
                              list(set.union(*[data[5] for data in values]))
                             )
                 for article_id, values in talk_data.items() if len(values) > 0}
    with open(TALK_DATA_FILE, 'w', encoding='utf8') as i:
        json.dump(talk_data, i, encoding='utf8', indent=2, ensure_ascii=False)