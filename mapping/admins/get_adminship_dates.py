import os
import json
from codecs import open
import requests
import re
from collections import OrderedDict

from bs4 import BeautifulSoup, Tag

from settings import DATA_FOLDER, LANGUAGE

OUTPUT_FILE = os.path.join(DATA_FOLDER, 'admin_dates.json')


def string_to_datetime(text):

    MONTH_DICT = {'janvier': '1', 'février': '2', 'mars': '3', 'avril': '4', 'mai': '5', 'juin': '6', 'juillet': '7', 'août': '8',
                   'septembre': '9', 'octobre': '10', 'novembre': '11', 'décembre': '12',
                   'januar': '1', 'februar': '2', 'märz': '3', 'april': '4', 'juni': '6', 'juli': '7', 'august': '8',
                   'september': '9', 'oktober': '10', 'november': '11', 'dezember': '12',
                   'january': '1', 'february': '2', 'march': '3', 'may': '5', 'june': '6', 'july': '7',
                   'october': '10', 'december': '12'}

    MONTH_DICT = OrderedDict(sorted(MONTH_DICT.items(), key=lambda t: len(t[0]), reverse=True))
    text = text.lower()

    rep = dict((re.escape(k), v) for k, v in MONTH_DICT.items())
    pattern = re.compile("|".join(rep.keys()))
    text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)

    coordinates = re.findall('[0-9]+', text)
    if len(coordinates) != 3:
        coordinates = [1] + coordinates
    return coordinates


def handle_en_page(url):
    r = requests.get(url)
    r.encoding = 'utf8'
    source = r.text
    soup = BeautifulSoup(source, 'lxml')
    adminships = []
    candidates = [tag for i, tag in enumerate(soup.find_all(goal_tags))]
    for candidate in candidates:
        tags = [content for content in candidate.contents if isinstance(content, Tag)]
        if [tag.name for tag in tags] == ['td'] * 4:
            name = name_from_en_tag(tags[0].a)
            date = tags[1].string
            adminship = (name, date)
            adminships.append(adminship)
    return adminships


def goal_tags(tag):
    return tag.name == 'tr'


def name_from_en_tag(tag):
    if tag.string is not None:
        name = tag.string
    else:
        name = tag.contents[0][0:-4]
    if name[-1] == '\n':
        return name[:-1]
    else:
        return name


def handle_fr_page(url):
    r = requests.get(url)
    r.encoding = 'utf8'
    source = r.text
    soup = BeautifulSoup(source, 'lxml')
    adminships = {}
    candidates = [tag for i, tag in enumerate(soup.find_all(goal_tags))]
    for candidate in candidates:
        if candidate.find_all('th'):
            continue

        if len(candidate.contents) == 18:
            name = candidate.find_all('td')[0].find('a').string
            date = candidate.find_all('td')[-1].find('a').string

        if len(candidate.contents) == 10:
            name = candidate.find_all('td')[0].find('a').string

            try:
                date = candidate.find_all('td')[1].find('a').contents[-1]
            except:
                date = candidate.find_all('td')[1].find('span').contents[-1]
        adminships[name] = date.replace('\xa0', ' ')
    return adminships


def handle_de_page(url):
    r = requests.get(url)
    r.encoding = 'utf8'
    source = r.text
    adminships = {}
    date = None
    name = None
    for l in source.split('\n'):
        if l.startswith('<ul><li><span id='):
            match = re.search('"></span>', l)
            if match:
                if date:
                    adminships[name] = date
                else:
                    print(name)
                name = (l[18:match.start()])
                name = name.replace('&#39', "'")
                date = None
            else:
                continue
        if 'Erstwahl' in l:
            match = re.search('[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{4}', l)
            if match:
                date = l[match.start():match.end()]
        if l == '<!-- ':
            break

    return adminships


if __name__ == '__main__':

    if LANGUAGE == 'EN':
        base_url = "https://en.wikipedia.org/wiki/Wikipedia:Successful_requests_for_adminship/"
        adminships = {}
        for year in range(2003, 2019):
            url = base_url + str(year)
            page_adminships = handle_en_page(url)
            for adminship in page_adminships:
                if adminship[0] not in adminships:
                    adminships[adminship[0]] = adminship[1]

    if LANGUAGE == 'FR':
        url = "https://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Liste_des_administrateurs"
        adminships = handle_fr_page(url)

    if LANGUAGE == 'DE':
        url = "https://de.wikipedia.org/wiki/Wikipedia:Administratoren/%C3%9Cbersicht"
        adminships = handle_de_page(url)

    adminships = {key: string_to_datetime(value) for key, value in adminships.items()}
    print(adminships)
    print(len(adminships))
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(adminships, f, ensure_ascii=False, indent=2)