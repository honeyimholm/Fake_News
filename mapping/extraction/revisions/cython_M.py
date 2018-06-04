# coding=utf8
from time import time
import os
import json

from settings import DATA_FOLDER, LOCAL_DATA_FOLDER, RAW_FOLDER
from src.mapping.extraction.revisions.get_M import file_iterator, get_M


SOURCE_FILE = os.path.join(LOCAL_DATA_FOLDER, '0520_reversions.txt')
OUTPUT_FILE = os.path.join(LOCAL_DATA_FOLDER, '0520_M.txt')
M_THRESHOLD = 2000


if __name__ == '__main__':
    conflicted = 0
    start_time = time()
    for i, (title, dump) in enumerate(file_iterator(SOURCE_FILE)):
        M, reversions = get_M(json.loads(dump))
        if M > M_THRESHOLD:
            print(title)
            print(M)
            conflicted += 1
        if i == 100000:
            print(time() - start_time)
            print(conflicted)
            break