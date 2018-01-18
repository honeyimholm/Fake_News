#TODO: this code copies from Fake_News\perspective\api_wrapper.py
import requests, json
import sqlite3

DATABASE_PATH = "D:\\WikiDB.db"
TOXICITY_THRESHOLD = .25

def toxicity_score(comment):
    url = 'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key=AIzaSyBVt6m1dQlYSuTLtRmKwU3onqjT7FaGeVs'
    payload_dict = {
      'comment': { 'text': comment },
      'requestedAttributes': {'TOXICITY': {}}
    }
    payload = json.dumps(payload_dict, ensure_ascii=False).encode("utf8")
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    r = requests.post(url, data=payload, headers=headers)
    response_dict = json.loads(r.text)
    return response_dict["attributeScores"]["TOXICITY"]["summaryScore"]["value"]

toxicity_dict = {}
#connect to db
conn = sqlite3.connect(DATABASE_PATH)
cur = conn.cursor()
#retrieve list of all articles
article_iterator = cur.execute("SELECT Count(*) FROM article")
#for every article retrieve all comments 
for article_row in article_iterator:
	print(article_row)
	break
	comments = ______
	toxic_comments = 0
	#add comment to dict if toxicity score above threshold
	for comment in _____:
		if(toxicity_score(comment)>TOXICITY_THRESHOLD):
			toxic_comments = toxic_comments+1
	if(toxic_comments>0):
		toxicity_dict[article] = toxic_comments
#export
with open('toxicity_dict.json', 'w') as fp:
    json.dump(toxicity_dict, fp)

#DEMO
#comment = "What kind of idiot name is foo — ?"
#print(toxicity_score(comment))