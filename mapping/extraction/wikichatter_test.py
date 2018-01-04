import wikichatter as wc
from pprint import pprint

text = open("sample_talk_page.txt").read()
pprint(wc.parse(text))