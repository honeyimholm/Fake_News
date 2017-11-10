import numpy as np
import json
from codecs import open
from time import time
import os

from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier

from settings import DATA_FOLDER

BAD_TRAIN = os.path.join(DATA_FOLDER, 'automated_bad.json')
GOOD_TRAIN = os.path.join(DATA_FOLDER, 'automated_good.json')
BAD_TEST = os.path.join(DATA_FOLDER, 'annotated_bad.json')
GOOD_TEST = os.path.join(DATA_FOLDER, 'annotated_good.json')
FINAL_INDEX_FILE = os.path.join(DATA_FOLDER, '2110_final_index.json')
TALK_DATA_FILE = os.path.join(DATA_FOLDER, '2110_talk_data.json')


if __name__ == '__main__':
    article_index = json.load(open(FINAL_INDEX_FILE, 'r', encoding='utf-8'), encoding='utf8')
    bad_train = json.load(open(BAD_TRAIN, 'r', encoding='utf-8'), encoding='utf8')
    good_train = json.load(open(GOOD_TRAIN, 'r', encoding='utf-8'), encoding='utf8')
    talk_data = json.load(open(TALK_DATA_FILE, 'r', encoding='utf-8'), encoding='utf8')

    bad_train = [talk_data[str(article_index[article])][0:-1] for article in bad_train if article in article_index and str(article_index[article]) in talk_data]
    good_train = [talk_data[str(article_index[article])][0:-1] for article in good_train if article in article_index and str(article_index[article]) in talk_data]

    x = np.array(bad_train + good_train)
    y = np.array(([1] * len(bad_train)) + ([0] * len(good_train)))

    clf = RandomForestClassifier(n_estimators=3, max_depth=None, min_samples_split=2, random_state=0)
    clf.fit(x, y)

    bad_test = json.load(open(BAD_TEST, 'r', encoding='utf-8'), encoding='utf8')
    good_test = json.load(open(GOOD_TEST, 'r', encoding='utf-8'), encoding='utf8')
    bad_test = [talk_data[str(article_index[article])][0:-1] for article in bad_test if article in article_index and str(article_index[article]) in talk_data]
    good_test = [talk_data[str(article_index[article])][0:-1] for article in good_test if article in article_index and str(article_index[article]) in talk_data]


    bad_probas = [data[1] for data in clf.predict_proba(bad_test)]
    bad_predictions = clf.predict(bad_test)
    good_probas = [data[1] for data in clf.predict_proba(good_test)]
    good_predictions = clf.predict(good_test)
    print str(sum(bad_probas)) + "/" + str(len(bad_test))
    print str(sum(good_probas)) + "/" + str(len(good_test))
    print str(sum(bad_predictions)) + "/" + str(len(bad_test))
    print str(sum(good_predictions)) + "/" + str(len(good_test))