import requests, json

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

comment = "What kind of idiot name is foo — ?"
print(toxicity_score(comment))