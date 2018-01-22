import os

dir = os.path.dirname(__file__)
DATA_FOLDER = os.path.join(dir, os.path.join('..', 'Wikidumps'))
RAW_FOLDER = os.path.join(DATA_FOLDER, 'raw')
API_KEY = open(os.path.join(RAW_FOLDER, 'API_KEY.txt')).read()