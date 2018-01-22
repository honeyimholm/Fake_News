import os
import json
import scipy.sparse as sp
import numpy as np
import subprocess

from settings import DATA_FOLDER

CLUSTER_DIRECTORY = "/home/teven/fake_news/Wikidumps/clusters/"
JSON_DIRECTORY = "/home/teven/fake_news/Wikidumps/analyzed_talk_pages/"

if __name__ == '__main__':

    for filename in os.listdir(CLUSTER_DIRECTORY):

        subprocess.check_output(['ls', '-la'])
        subprocess.check_output(['/home/teven/grawitas/bin/./grawitas_cli_xml_to_db',
                                 '-i /home/teven/grawitas/bin/smaller_dump.txt',
                                 '-o out_sqlite3.db',])

        subprocess.check_output(['/home/teven/grawitas/bin/./grawitas_cli_db_export',
                                 '--sqlite-file /home/teven/fake_news/Wikidumps/WikiDB.db',
                                 '--article-filter-file ' + CLUSTER_DIRECTORY + filename,
                                 '--comment-list-csv ' + JSON_DIRECTORY + filename[:-4] + '_comments.csv'])
