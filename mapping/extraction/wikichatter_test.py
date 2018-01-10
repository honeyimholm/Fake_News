import json
import wikichatter as wc
from pprint import pprint

text = open("sample_talk_page.txt").read()
pprint(wc.parse(text))
json.dump(wc.parse(text), open("example.json", 'w'), ensure_ascii=False, indent=2)