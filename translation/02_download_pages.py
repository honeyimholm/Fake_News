from util_wikiapi import *
from myconfig import *
import wikipedia as wiki
import time
import pickle


f = file(catname+'.txt')
namelist = [ l.strip() for l in f]

#corpus = pickle.load(open('multilingual_corpus.pkl','rb'))
corpus ={}

try:
    for name in namelist:
        try:
            if name in corpus.keys(): continue
            corpus[name] = {}
            wiki.set_lang('en')
            #pg = wiki.page(name)
            pg = wiki.search(name)
            if type(pg) is list: pg = wiki.page(pg[0])
            #if type(pg) is list: pg = wiki.search(pg[0])
            corpus[name]['en'] = pg.content.encode('utf-8')
            total_char_num = len(pg.content)
            en_title = pg.url.split('/')[-1]
            en_title = en_title.replace(' ','%20')
            mllst = get_language_links(en_title)
            print en_title, len(mllst)
            for link in mllst:
                if link['lang'] in langlst: 
                    wiki.set_lang(link['lang'])
                    pg = wiki.page(link['*'])
                    if type(pg) is list: continue
                    corpus[name][link['lang']] = pg.content.encode('utf-8')
                    #corpus[name][link['lang']] = pg.summary.encode('utf-8')
        except:
            continue
except IOError:
    print corpus
    pickle.dump(corpus, open(catname+'.pkl','wb'))
pickle.dump(corpus, open(catname+'.pkl','wb'))
