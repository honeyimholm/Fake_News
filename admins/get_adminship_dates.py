import os
import json
from codecs import open
import requests

from bs4 import BeautifulSoup, Tag

from settings import DATA_FOLDER

OUTPUT_FILE = os.path.join(DATA_FOLDER, 'admin_dates.json')


def handle_page(url):
    r = requests.get(url)
    r.encoding = 'utf8'
    source = r.text
    soup = BeautifulSoup(source, 'lxml')
    adminships = []
    candidates = [tag for i, tag in enumerate(soup.find_all(goal_tags))]
    for candidate in candidates:
        tags = [content for content in candidate.contents if isinstance(content, Tag)]
        if [tag.name for tag in tags] == ['td'] * 4:
            name = name_from_tag(tags[0].a)
            date = tags[1].string
            adminship = (name, date)
            adminships.append(adminship)
    return adminships


def goal_tags(tag):
    return tag.name == 'tr'


def name_from_tag(tag):
    if tag.string is not None:
        return tag.string
    else:
        return tag.contents[0][0:-4]


if __name__ == '__main__':
    base_url = "https://en.wikipedia.org/wiki/Wikipedia:Successful_requests_for_adminship/"
    adminships = {}
    for year in range(2003, 2018):
        url = base_url + str(year)
        page_adminships = handle_page(url)
        for adminship in page_adminships:
            if adminship[0] not in adminships:
                adminships[adminship[0]] = adminship[1]
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(adminships, f, encoding='utf8', ensure_ascii=False, indent=2)