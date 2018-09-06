# coding=utf8
import json
import os
import sqlite3
import re
import time
import xml.etree.ElementTree as etree

from settings import INTERLINGUAL_FOLDER, SUPPORTED_LANGUAGES, DATA_FOLDER, RAW_FOLDER
from mapping.extraction.links.index_links import article_generator

SOURCE_FILE = os.path.join(RAW_FOLDER, 'enwiki-20180520-pages-meta-current.xml')
TRANSLATION_LANGUAGES = [language_code.lower() for language_code in SUPPORTED_LANGUAGES if language_code != 'EN']
TRANSLATION_FILE = os.path.join(INTERLINGUAL_FOLDER, 'translation_index.json')

DATABASE_PATH = os.path.join(INTERLINGUAL_FOLDER, 'enwiki-20180620-langlinks.db')
conn = sqlite3.connect(DATABASE_PATH)
cur = conn.cursor()


def merge_redirects(redirects, translations):

    return {article: translations[redirect] for article, redirect in redirects.items() if redirect in translations}


if __name__ == '__main__':

    translation_dictionary = {}
    for language_code in TRANSLATION_LANGUAGES:
        references = cur.execute("SELECT ll_from, ll_title from langlinks WHERE ll_lang='{}'".format(language_code))
        references = references.fetchall()
        translation_dictionary[language_code] = {reference[0]: reference[1] for reference in references}

    article_number = 0
    start_time = time.time()
    en_translations = {language_code.lower(): {} for language_code in TRANSLATION_LANGUAGES}
    redirect_references = {}
    for i, (title, article_id, text, redirect) in enumerate(article_generator(SOURCE_FILE)):
        if i % 10000 == 0:
            print(i)
            print(time.time() - start_time)
        if redirect:
            redirect_references[title] = text
        else:
            redirect_references[title] = title

            for language_code in TRANSLATION_LANGUAGES:
                try:
                    en_translations[language_code][title] = translation_dictionary[language_code][article_id]
                except KeyError:
                    pass

    final_translations = {language: merge_redirects(redirect_references, translations) for language, translations in en_translations.items()}

    with open(TRANSLATION_FILE, 'w', encoding='utf8') as i:
        json.dump(final_translations, i, indent=2, ensure_ascii=False)
