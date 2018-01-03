import wikichatter as wc

text = open("sample_talk_page.txt").read()
print(wc.parse(text))