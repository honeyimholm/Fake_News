import os


dir = os.path.dirname(__file__)
LOCAL_DATA_FOLDER = os.path.join(dir, os.path.join('..', 'Wikidumps'))
DISK_DATA_FOLDER = '/media/teven/TOSHIBA/Wikidumps/'

SUPPORTED_LANGUAGES = ['EN', 'FR', 'DE']
LANGUAGE = "DE"

if LANGUAGE not in SUPPORTED_LANGUAGES:
    raise ValueError('Language {} not supported'.format(LANGUAGE))
if LANGUAGE == "EN":
    LANGUAGE_FOLDER = os.path.join(DISK_DATA_FOLDER, 'en')
if LANGUAGE == "FR":
    LANGUAGE_FOLDER = os.path.join(DISK_DATA_FOLDER, 'fr')
if LANGUAGE == "DE":
    LANGUAGE_FOLDER = os.path.join(DISK_DATA_FOLDER, 'de')

DATA_FOLDER = os.path.join(LANGUAGE_FOLDER, 'processed')
RAW_FOLDER = os.path.join(LANGUAGE_FOLDER, 'raw')
API_KEY = open(os.path.join(DISK_DATA_FOLDER, 'API_KEY.txt')).read()

print(LANGUAGE)
