# coding=utf8
import xml.etree.ElementTree as etree
import time
import os
import re
import json
from codecs import open

from settings import DATA_FOLDER
from settings import RAW_FOLDER

SOURCE_FILE = os.path.join(RAW_FOLDER, 'dewiki-20180620-pages-meta-current.xml')
DISAMBIGUATION_FILE = os.path.join(RAW_FOLDER, 'disambiguations.json')
OUTPUT_FILE = os.path.join(DATA_FOLDER, 'links.txt')
INDEX_FILE = os.path.join(DATA_FOLDER, 'index.json')
FINAL_INDEX_FILE = os.path.join(DATA_FOLDER, 'final_index.json')
REDIRECT_FILE = os.path.join(DATA_FOLDER, 'redirects.json')

DISAMBIGUATION_NAMES = set(json.load(open(DISAMBIGUATION_FILE, 'r', encoding='utf8'), encoding='utf8'))
LINK_PATTERN = re.compile("\[\[(.+?)\]\]")
REF_PATTERN = re.compile("<ref>.*</ref>")
PRUNED_KEYS = ['Category:', 'File:', 'Template:', 'Portal:', 'Draft:', 'MediaWiki:', 'List of', 'Wikipedia:', 'TimedText:',
               'Help:', 'Book:', 'Module:', 'Topic:']


def strip_tag_name(t):
    t = t.split('}')[1]
    return t


def article_generator(file):

    redirect = False
    not_article = False
    yielded = 0

    generator = etree.iterparse(file, events=('start', 'end'))
    _, root = next(generator)

    for event, elem in generator:
        xml_tag = strip_tag_name(elem.tag)

        if event == 'start':
            if xml_tag == 'page':
                title = None
                article_id = None
                text = None
                revision = False
                redirect = False
                not_article = False
            elif xml_tag == 'revision':
                revision = True

        else:
            if not_article:
                continue
            if xml_tag == 'title':
                title = elem.text
                if is_to_prune(title) or "(disambiguation)" in title or title in DISAMBIGUATION_NAMES:
                    not_article = True
            if xml_tag == 'id' and not revision:
                article_id = int(elem.text)
            if xml_tag == 'redirect':
                text = elem.attrib['title']
                redirect = True
            if not redirect and xml_tag == 'text':
                text = elem.text
            if xml_tag == 'ns' and elem.text != '0':
                not_article = True
            if xml_tag == 'page':
                if title and article_id and text:
                    yield title, article_id, text, redirect
                    yielded += 1
                    root.clear()


def clean_links(links):
    return [link.split('|')[0].split('#')[0] for link in links if ":" not in link and len(link.split('|')) < 2 and len(link.split('|')[0].split('#')[0]) > 0]


def remove_ref_tags(text):
    return re.sub(REF_PATTERN, "", text)


def is_to_prune(title):
    return any([title.startswith(key) for key in PRUNED_KEYS])


if __name__ == '__main__':
    article_number = 0
    start_time = time.time()
    article_indexes = {}
    redirect_references = {}
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for i, (title, id, text, redirect) in enumerate(article_generator(SOURCE_FILE)):
            if i % 10000 == 0:
                print(i)
                print(time.time() - start_time)
            if redirect:
                redirect_references[title] = text
            else:
                f.write(title + "\n")
                links = re.findall(LINK_PATTERN, text)
                for link in clean_links(links):
                    f.write(link + "\n")
                f.write("\n")
                article_indexes[title] = article_number
                redirect_references[title] = title
                article_number += 1
    print("dumping index dict")
    with open(INDEX_FILE, 'w', encoding='utf-8') as g:
        json.dump(article_indexes, g, indent=2, ensure_ascii=False)
    print("indexes dumped in " + str(time.time() - start_time))
    with open(REDIRECT_FILE, 'w', encoding='utf-8') as h:
        json.dump(redirect_references, h, indent=2, ensure_ascii=False)
    print("redirects dumped in " + str(time.time() - start_time))
    final_index = {article: article_indexes.get(redirect, None) for article, redirect in redirect_references.items()}
    with open(FINAL_INDEX_FILE, 'w', encoding='utf8') as i:
        json.dump(final_index, i, indent=2, ensure_ascii=False)