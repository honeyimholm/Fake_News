import json
 
with open('article_index.json', 'r+') as f:
     dict = json.load(f, encoding='utf8')
     json.dump(f, dict, encoding='utf8', indent=2)
