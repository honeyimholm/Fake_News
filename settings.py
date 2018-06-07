import os

dir = os.path.dirname(__file__)
LOCAL_DATA_FOLDER = os.path.join(dir, os.path.join('..', 'Wikidumps/2018_processed'))
DATA_FOLDER = '/media/teven/TOSHIBA/Wikidumps/2018_processed'
RAW_FOLDER = '/media/teven/TOSHIBA/Wikidumps/raw'
API_KEY = open(os.path.join(RAW_FOLDER, 'API_KEY.txt')).read()