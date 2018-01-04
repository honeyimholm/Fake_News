import os
import math
import sys
import argparse
import wikipedia
import nltk
import string
import matplotlib.pyplot as plt
from nltk.tokenize import sent_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

#helper function to truncate titles
def smart_truncate(content, length=50, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return content[:length].rsplit(' ', 1)[0]+suffix


#if __name__ == '__main__':
def main():


    parser = argparse.ArgumentParser()
    parser.add_argument('-l','--lang', help='which language to crawl', required=True)
    parser.add_argument('-n','--num', type=int, help='the number of pages to crawl for each category', required=True)
    parser.add_argument('-c','--cat', help='which category to crawl', required=True)
    args = vars(parser.parse_args())
    cat = args['cat']
    lang = args['lang']
    num = args['num']
    directory = './acl2017_data'
    if not os.path.exists(directory):
        os.makedirs(directory)
    #set up the category page
    c_file = open("C:\\Users\sahol\Desktop\Fake News Deep Learning\Wikipedia_title_dataset-master\category_list_en.txt","w")
    c_file.write(cat)
    c_file.close()
    #Crawling wiki
    print("Crawling..." + lang + " wikipedia")
    os.system('python WikiCrawler.py -l ' + lang + ' -n ' + str(num))

    #raw dictionary to txt file
    print("Raw to Format...")
    os.system('python raw2format.py -l ' + lang)

    #take category title outputs and extract raw text
    dir = os.path.dirname(os.path.abspath(__file__))
    print("dir: " + dir)
    filename = dir + r'\acl2017_data\en.txt'
    print(filename)
    f = open(filename,"r")
    content = f.readlines()
    if(len(content)<100):
        return "Not enough articles - " + str(len(content))

    #formats the text file output to only contain the titles
    for idx, line in enumerate(content):
        content[idx] = ' '.join(line.split()[1:])
    #print content

    #TODO: parallelize here
    #TODO: remove later parts of wikipedia articles for increased accuracy
    #use wikipedia library to extract text and run nltk semantic parsing
    printable = set(string.printable)
    article_score_dict = {}
    for idx, title in enumerate(content):
        try:
            page = wikipedia.page(title) 
            print(page.title)
            p = page.content
            p = [x for x in p if x in printable]
            sent_tokenize_list = sent_tokenize(p)
            print(sent_tokenize_list)
        except:
            #most errors taken care of by printable filter
            #sometimes get page not found error
            #sometimes get page disambiguation error
            continue
        sid = SentimentIntensityAnalyzer()
        #TODO make sum a prettier lambda
        score_mean = 0
        score_variance = 0
        sentences = 0
        for sentence in sent_tokenize_list:
            print(sentence)
            ss = sid.polarity_scores(sentence)
            #score = score + ss["pos"] - ss["neg"]
            #process: 
                #main control reads in one item from category
                #main control opens crawl with argument of category
                #if there aren't 100 articles in the category then terminate the search and remove the category from the category list
                #crawl runs sentiment analysis to find the running positive and negative scores, as well as article level sentiment variance for a category 
                #the two metrics are piped back to main control by means of a queue
                #TODO if the metrics are reported back as "remove" then remove
                #else store the metrics in a file 
                #TODO store metrics in more univeral way like sqlite or JSON
            #here we'll add positive and negative scores to get a sentiment bias
            score_mean = score_mean + ss["pos"] - ss["neg"]  
            sentences = sentences+1
            for k in sorted(ss):
                print('{0}: {1}, '.format(k, ss[k]))
        score_mean = score_mean/(2*sentences)
        for sentence in sent_tokenize_list:
            ss = sid.polarity_scores(sentence)
            score_variance = score_variance + (ss["pos"]-score_mean)**2
            score_variance = score_variance + (ss["neg"]-score_mean)**2
        score_variance = score_variance/(2*sentences)
        #divide by 2*sentences since treating each pos and neg as inputs
        #graphing variance for now 
        score = score_variance
        #unicode title characters will cause errors in plotting
        formatted_title = smart_truncate([x for x in title if x in printable])
        article_score_dict[formatted_title] = round(score,3)
        if(idx==150):
            break


    #this section takes the article score dictionary and plots it
    #   from lowest to highest bias
    sorted_values = list(article_score_dict.values())
    sorted_values.sort()
    shortened_titles = list(article_score_dict.keys())
    print(sorted_values) 
    plt.bar(list(range(len(article_score_dict))), sorted_values, align="center")
    plt.xticks(list(range(len(article_score_dict))), list(article_score_dict.keys()), rotation="vertical")
    plt.tight_layout()
    plt.show()
    #plt.savefig(category)
main()

#TODO
#implement category line counting 
