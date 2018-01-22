# coding=utf8
import xml.etree.ElementTree as etree
import time
import os
import re
import json
import string
import numpy as np
import wikichatter as wc
from multiprocessing import Pool
from codecs import open
import requests

from api_wrapper import toxicity_score
from settings import DATA_FOLDER
from settings import RAW_FOLDER

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


def toxicity_number(section):
    toxicity = 0
    if "author" in section and "time_stamp" in section and "text_blocks" in section:
        text_blocks = [text[1:-1] for text in section['text_blocks']]
        pruned_blocks = [comment_text for comment_text in text_blocks
                         if len(comment_text) > 20 and (comment_text[0] != '"' or comment_text[-1] != '"')]
        if any([toxicity_score(comment) > 0.2 for comment in pruned_blocks]):
            toxicity = 1
    for reply in section['comments']:
        toxicity += toxicity_number(reply)
    return toxicity


# def toxicity_explorer(parsed_text):
#     if "author" in parsed_text and "time_stamp" in parsed_text and "text_blocks" in parsed_text:
#         text_blocks = [text[1:-1] for text in parsed_text['text_blocks']]
#         pruned_blocks = [comment_text for comment_text in text_blocks
#                          if len(comment_text) > 20 and (comment_text[0] != '"' or comment_text[-1] != '"')]
#         toxicity = sum(toxicity_score(comment_text for comment_text in pruned_blocks))
#         length = sum(len([comment_text for comment_text in pruned_blocks]))
#         if length > 0:
#             yield toxicity
#     for comment in parsed_text:
#         for toxicity in toxicity_explorer(comment['comments']):
#             yield toxicity


def handle_article(article):

    title, text = article[0], article[1]

    article_id = article_index.get(title, None)

    try:
        parsed_text = (wc.parse(text))
    except wc.error.MalformedWikitextError:
        print(text)
        print(title)
        raise wc.error.MalformedWikitextError
    if len(parsed_text) > 1:
        print(parsed_text)
        raise NameError('several sections in dict')
    else:
        parsed_text = parsed_text['sections']

    return article_id, sum(toxicity_number(section) for section in parsed_text)


if __name__ == '__main__':
    pool = Pool(4)
    problems = 0
    talk_data = {article_id: 0 for article_id in list(article_index.values())}

    print('starting')
    start_time = time.time()
    for i, (article_id, toxicity_number) in enumerate(pool.imap_unordered(handle_article, article_generator(SOURCE_FILE))):
        if article_id is None:
            problems += 1
            continue
        else:
            talk_data[article_id] += toxicity_number
        if i % 10000 == 0:
            print(str(i - problems) + "/" + str(i))
            print(str(time.time() - start_time) + "s")
    with open(TALK_DATA_FILE, 'w', encoding='utf8') as i:
        json.dump(talk_data, i, encoding='utf8', indent=2, ensure_ascii=False)
