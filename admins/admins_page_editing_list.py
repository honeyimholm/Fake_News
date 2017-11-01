import sys
import urllib2
import urllib
import json
import time
import numpy as np
from collections import defaultdict
from bs4 import BeautifulSoup
import gensim
from sklearn.cluster import KMeans
import time


base = 'https://en.wikipedia.org/'
### e.x. 2015-08-13T17:53:16Z
def str2timestamp(s):
    yr, mth, d = s.split('T')[0].split('-')
    hr, minu, sec = s.split('T')[1].split('Z')[0].split(':')
    return int(yr), int(mth), int(d), int(hr), int(minu), int(sec)

def timestamp2str(yr, mth, d, hr, minu, sec):
    return str(yr)+'-'+str(mth)+'-'+str(d)+'T'+str(hr)+':'+str(minu)+':'+str(sec)+'Z'

###
def time_diff_in_sec(s1,s2):
    t1 = time.strptime(s1, '%Y-%m-%dT%H:%M:%SZ')
    t2 = time.strptime(s2, '%Y-%m-%dT%H:%M:%SZ')
    t1 = time.mktime(t1)
    t2 = time.mktime(t2)
    return t1-t2

"""
Revision Analysis
"""
def get_revisions_from_pgid(pgid, rvsize=50):
    rvlimit = 50
    lasttime = None
    revisions = []
    for i in range(rvsize/rvlimit+1):
        query = '/w/api.php?action=query&format=json&pageids='+pgid+'&prop=revisions&rvprop=ids|flag|timestamp|comment|user|size&rvlimit=50'
        if lasttime is not None: query+='&rvstart='+lasttime
        url = base+query
        try:
            response = urllib.urlopen(url)
            pages = json.loads(response.read())
            revisions+=pages['query']['pages'][pgid]['revisions'][1:]
            lasttime = pages['query']['pages'][pgid]['revisions'][-1]['timestamp']
        except urllib2.HTTPError: # 404, 500, etc..
            pass
    return revisions

def get_user_dict(revisions):
    userdict = defaultdict(int)
    for i,r in enumerate(revisions):
        if 'user' not in r.keys(): continue
        userdict[r['user']]+=1
    return userdict

def get_revert_num(revisions):
    num = 0
    for i,r in enumerate(revisions):
        if 'comment' not in r.keys(): continue
        comment = r['comment'].lower()
        if 'revert' in comment or 'undid' in comment: num+=1
    return num

def get_revision_frequency(revisions):
    s1 = revisions[0]['timestamp']
    s2 = revisions[-1]['timestamp']
    d = time_diff_in_sec(s1,s2)
    #print s1,s2,d
    d = float(d)/86400.0  ### difference in days
    if d==0: return 0
    else: return len(revisions)/d

"""
User contribution analysis
"""
def get_random_userid():
    ### get random page id
    randomid = get_random_pageid()

    ### get a random user from that page
    query = '/w/api.php?action=query&&format=json&prop=revisions&pageids='+str(randomid)+'&rvprop=user'
    url = base+query
    try:
        response = urllib.urlopen(url)
        response = json.loads(response.read())
        uid = response['query']['pages'][str(randomid)]['revisions'][0]['user']
    except urllib2.HTTPError:
        pass
    return uid

def get_user_contribs(user, ucsize=50):
    uclimit = 50
    lasttime = None
    contribs = []
    for i in range(ucsize/uclimit+1):
        query = '/w/api.php?action=query&list=usercontribs&format=json&ucuser='+user+'&uclimit='+str(uclimit)+'&ucprop=ids|title|timestamp|sizediff|comment|size|tags'
        if lasttime is not None: query+='&rcstart='+lasttime
        url = base+query
        try:
            response = urllib.urlopen(url)
            contributs = json.loads(response.read())
            contribs_batch = contributs['query']['usercontribs']
            if i!=0: contribs_batch = contribs_batch[1:]
            contribs+=contributs['query']['usercontribs']
            lasttime = contributs['query']['usercontribs'][-1]['timestamp']
        except urllib2.HTTPError:
            pass
    return contribs

#def hand_craft_contribtype(contrib):
    

def suggest_cat(title):
    query = '/w/api.php?action=query&format=json&titles='+title+'&prop=categories'
    url = base+query
    try:
        response = urllib.urlopen(url)
        response = json.loads(response.read())
        lst = [cat['title'] for cat in response['query']['pages'].values()[0]['categories']]
    except urllib2.HTTPError, AttributeError:
        print 'error'
        return []
        pass
    except KeyError:
        print 'key error'
        return []
        pass
    return lst
    
def accumulate_cat(cat_dict, catlst):
    if len(cat_dict.keys())==0: cat_dict = defaultdict(int)
    for cat in catlst:
        cat_dict[cat]+=1
    return cat_dict

def get_random_pageid():
    query = '/w/api.php?action=query&format=json&list=random&rnlimit=2'
    url = base+query
    try:
        response = urllib.urlopen(url)
        response = json.loads(response.read())
        randomid = response['query']['random'][0]['id']
    except urllib2.HTTPError:
        pass
    return randomid

def to_utf8(text):
    if isinstance(text, unicode):
        # unicode to utf-8
        return text.encode('utf-8')
    else:
        # maybe utf-8
        return text.decode('utf-8').encode('utf-8')

def crawl_cat(category):
    query = '/w/api.php?action=query&format=json&prop=&list=categorymembers'+ \
            '&meta=&cmtitle='+category+'&cmprop=ids%7Ctitle%7Ctype' +\
            '&cmtype=page%7Csubcat&cmlimit=max'
    url = base+query
    try:
        response = urllib.urlopen(url)
        response = json.loads(response.read())
        subcatlst = [ obj['title'] for obj in response['query']['categorymembers'] if obj['type']=='subcat']
    except urllib2.HTTPError:
        pass
    return subcatlst

"""
generate wiki category list recursively
"""
def generate_cat_list(category,limit,acculst=[],queue=[]):
    if len(acculst)>limit: return acculst
    subcatlst = crawl_cat(category)
    acculst+=subcatlst
    queue+=subcatlst
    cat = queue.pop(0)
    return generate_cat_list(cat,limit,acculst,queue)

"""
generate wiki catetory leaf nodes set recursively
"""
def generate_leaves_list(category,limit,acculst=[]):
    if len(acculst)>limit: return [category]+acculst
    subcatlst = crawl_cat(category)
    acculst+=subcatlst
    cat = acculst.pop(0)
    return generate_leaves_list(cat,limit,acculst)
    

def cat_trace(title,limit,acculst=[],queue=[]):
    if special_cat_check(title): return acculst
    if len(acculst)>limit: return acculst
    catlst = suggest_cat(title)
    acculst+=catlst
    queue+=catlst
    if len(queue)==0: return acculst
    cat = queue.pop(0)
    while special_cat_check(cat) and len(queue)>0:
        cat = queue.pop(0)
    return cat_trace(cat,limit,acculst,queue)

def special_cat_check(title):
    title = title.lower()
    if 'all' in title: return True
    if 'establishments' in title: return True
    if 'accuracy' in title: return True
    if 'article' in title: return True
    if 'diffusion' in title: return True
    if 'main' in title: return True
    if 'redirect' in title: return True
    #print 'pass check', title
    return False


def get_diff(parentid,revid):
    query = '/w/api.php?action=compare&fromrev='+str(parentid)+'&torev='+str(revid)+'&format=json'
    url = base+query
    difftext = None
    try:
        response = urllib.urlopen(url)
        pages = json.loads(response.read())
        difftext = pages['compare']['*']

    except urllib2.HTTPError: # 404, 500, etc..
        pass
    except KeyError:
        pass
    except ValueError:
        pass
    return difftext

def get_user_props(userid):
    query = '/w/api.php?action=query&list=users&ususers='+userid+'&usprop=blockinfo|groups|editcount|registration|emailable|gender&format=json'
    url = base+query
    try:
        response = urllib.urlopen(url)
        userinfos = json.loads(response.read())
        userinfos = userinfos['query']['users'][0]
    except urllib2.HTTPError: # 404, 500, etc..
        pass
    return userinfos

"""
cat_dict -- category contribution dictionary
"""
def cat_entropy(cat_dict,catnum):
    pdfvec = np.zeros((catnum,))
    for i,key in enumerate(cat_dict.keys()):
        pdfvec[i] = cat_dict[key]
    pdfvec/=np.sum(pdfvec)
    pdfvec+=0.001
    pdfvec/=np.sum(pdfvec)
    S = -np.sum(pdfvec * np.log(pdfvec), axis=0)
    return S

def user_feature1(edit_featmat):
    return edit_featmat.mean(axis=0)
    
"""
blocked user analysis
"""
def get_blocked_list(num=100,starttime=None):
    query = '/w/api.php?action=query&list=blocks&bkprop=id|user|by|timestamp|expiry|reason|range|flags&bklimit='+str(num)+'&format=json'
    if starttime is not None:
        query+='&bkstart='+str(starttime)
    url = base+query
    try:
        response = urllib.urlopen(url)
        blockinfos = json.loads(response.read())
        blockinfos = blockinfos['query']['blocks']
    except urllib2.HTTPError: # 404, 500, etc..
        pass

    return blockinfos

"""
Multi-lingual comparison
"""
def get_language_links(pgname):
    query = '/w/api.php?action=query&titles='+pgname+'&prop=langlinks&lllimit=500&format=json'
    url = base+query
    try:
        response = urllib.urlopen(url)
        langinfo = json.loads(response.read())
        mllist = langinfo['query']['pages'].values()[0]['langlinks']

    except urllib2.HTTPError: # 404, 500, etc..
        pass
    return mllist

'''
parse wiki content into paragraph dictionary
'''
def parse_wiki_content(text):
    topic_stack = ['== Summary ==']
    depth_stack = ['10']
    sentlst = []
    paragraph_dict = {}
    for line in text.split('\n'):
        if '==' in line:
            if len(sentlst)>0: 
                paragraph_dict[''.join(topic_stack)] = '\n'.join(sentlst)
                sentlst = []
            depth = line.index(' ')
            while len(depth_stack)>0 and depth_stack[-1]>=depth:
                topic_stack.pop(-1)
                depth_stack.pop(-1)
            topic_stack.append(line.strip())
            depth_stack.append(depth)
            print topic_stack
        else:
            sentlst.append(line)
    if len(sentlst)>0:
        paragraph_dict[''.join(topic_stack)] = '\n'.join(sentlst)
    return paragraph_dict

if __name__=='__main__':
    #BRIEF: get admin and make sure they have more than 1000 contributions
    contribs = []
    admins_list = []
    with open('parsed_admin_list_english.txt') as f:
        admins_list = f.readlines()

    #admins_list = open("parsed_admin_list_english.txt","r")
    #while len(contribs)<1000:
    admin_dict = {}
    for admin in admins_list:
    #user_id =admins_list.readline()
        user_id = admin
        print "Checking: " + user_id
        contribs = get_user_contribs(user_id, 1000)
            #user_id = get_random_userid()
        #filter for additions of at least 1 sentence
        #print user_id + "has more than 1000 contributions"
        user_articles = []
        for c in contribs:
            if(c["title"].find("User")==-1):
                user_articles.append(to_utf8(c["title"]))
        admin_dict[admin] = user_articles
        #remove this to process ALL admins in admin list
        break
    json.dump(admin_dict, open('admin_dict.json', 'r'), indent=2, encoding='utf8', ensure_ascii=False)