# coding=utf8
from googleapiclient import discovery, errors
from time import sleep

from settings import API_KEY


LENGTH_THRESHOLD = 3000


def toxicity_score(comment):
    for i in range(100):
        try:
            if len(comment) > LENGTH_THRESHOLD:
                return -1
            service = discovery.build('commentanalyzer', 'v1alpha1', developerKey=API_KEY)
            analyze_request = {
              'comment': { 'text': comment },
              'requestedAttributes': {'TOXICITY': {}}
            }
            try:
                response = service.comments().analyze(body=analyze_request).execute()
            except errors.HttpError:
                return -1
            return response["attributeScores"]["TOXICITY"]["summaryScore"]["value"]
        except:
            print("Toxicity API unresponsive ; retrying in " + str(4*i*i) + "s")
            sleep(4*i*i)

if __name__ == '__main__':
    comment = "friendly greetings from python"
    print(toxicity_score(comment))
    comment = "What kind of idiot name is foo — ?"
    print(toxicity_score(comment))
    comment = "2013â?"
    print(toxicity_score(comment))