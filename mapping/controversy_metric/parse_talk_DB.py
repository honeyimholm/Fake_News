# coding=utf8
import requests, json
import os
import sqlite3
from multiprocessing import Pool
from time import time
import numpy as np
import matplotlib.pyplot as plt

from settings import DATA_FOLDER
from toxicity_api_wrapper import toxicity_score

DATABASE_PATH = os.path.join(DATA_FOLDER, 'WikiDB.db')
TOXICITY_THRESHOLD = .25
toxicity_dict = {}
conn = sqlite3.connect(DATABASE_PATH)
cur = conn.cursor()


def handle_comment(comment_row):
    print(comment_row)
    article_id, text = comment_row[0], comment_row[1]
    start_tox = time()
    if toxicity_score(text) > TOXICITY_THRESHOLD:
        toxic = True
    else:
        toxic = False
    print(time() - start_tox)
    return article_id, toxic


def article_iterator_wrapper(comment_iterator):
    comments = []
    current_id = 1
    for article_id, comment in comment_iterator:
        if article_id == current_id:
            comments.append(comment)
        else:
            yield current_id, comments
            current_id = article_id
            comments = [comment]


if __name__ == '__main__':
    comment_iterator = cur.execute("SELECT article_id, text from comment ORDER BY article_id")
    start_time = time()
    total_comments = 0
    max_comments = 0
    comment_distribution = np.zeros(47628)
    # pool = Pool(1)

    for i, (current_id, comments) in enumerate(article_iterator_wrapper(comment_iterator)):
        talk_length = len(comments)
        total_comments += talk_length
        comment_distribution[talk_length - 1] += 1
        if talk_length > max_comments:
            max_comments = talk_length
        if i % 1000 == 0:
            print(time()-start_time)
            print(i)


    print(max_comments)
    print(total_comments / float(i))


    # for i, (article_id, toxic) in enumerate(map(handle_comment, comment_iterator)):
    #     print(i)
    #     if i % 100 == 0:
    #         print(i)
    #         print(time() - start_time)
    #         if i > 0:
    #             break

    # with open('toxicity_dict.json', 'w') as fp:
    #     json.dump(toxicity_dict, fp)
