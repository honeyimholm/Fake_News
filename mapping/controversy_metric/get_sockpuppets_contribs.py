import json
import os
import requests
from time import time, sleep
import re
 
from settings import DATA_FOLDER
from get_sockpuppets import query


def get_contribs(user_names, contrib_dict):

    for result in query({'list': 'usercontribs', 'ucprop': 'title|sizediff', 'uclimit': 'max', 'ucuser': user_names, 'ucnamespace': '0|1', 'ucshow': '!minor'}):

        for contrib in result['usercontribs']:
            try:
                try:
                    contrib_dict[contrib['user']] += (contrib['title'], contrib.get('sizediff', 0))
                except KeyError:
                    contrib_dict[contrib['user']] = [(contrib['title'], contrib.get('sizediff', 0))]
            except KeyError:
                continue


def remove_user_heading(page_title):
    if page_title.startswith('User:'):
        return page_title[5:]
    if page_title.startswith('User talk:'):
        return page_title[10:]


def clean_backslashes(user_name):
    if user_name.startswith('User:'):
        user_name = user_name[5:]
    return user_name.split('/')[0]


if __name__ == '__main__':

    sockpuppet_dictionary = json.load(open(os.path.join(DATA_FOLDER, 'sockpuppets_1605.json')))

    start_time = time()

    print(len(sockpuppet_dictionary))

    contrib_dict = {}

    for i, (user, sockpuppets) in enumerate(sockpuppet_dictionary.items()):

        final_list = list({clean_backslashes(user_name) for user_name in sockpuppets + [user] if user_name is not None})
        sock_number = len(final_list)
        sock_index = 0
        contrib_dict[user] = {}

        while sock_index < sock_number:

            try:
                pipe_delimited_user_names = "|".join(final_list[sock_index:sock_index + 50])
                try:
                    get_contribs(pipe_delimited_user_names, contrib_dict[user])
                except requests.exceptions.HTTPError as e:
                    print(e)
                    print(pipe_delimited_user_names)
            except TypeError:
                print("User " + user + " has None associated")

            sock_index += 50

        if i % 50 == 0:

            print(i)
            print(time() - start_time)

    json.dump(contrib_dict, open(os.path.join(DATA_FOLDER, 'sockpuppet_contributions_1605.json'), 'w'), indent=2, ensure_ascii=False)
