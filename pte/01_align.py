import sys
from text_aligner import *
import pickle
import nltk
from scipy.optimize import linear_sum_assignment

def str2utf8(s): return unicode(s,'utf-8')

def extract_summary(sentlst):
    lst = []
    for s in sentlst:
        if s[0]=='=': break
        lst.append(s)
    return lst

#f = file('translated_corpus.pkl','rb')
f = file('translated_Wars.pkl','rb')
corpus = pickle.load(f)
#corpus.pop('Donald Trump')
f.close()

#testlst = ['Akio Toyoda']
#testlst = ['Xi Jinping']
for key in corpus.keys():
#for key in testlst:
    page_dict = corpus[key]
    en_page = unicode(page_dict['en'],'utf-8')
    key = unicode(key,'utf-8')
    print key
    en_sent_lst = sent_tokenize(en_page)
    en_sent_lst, en_title_lst = title_struct_feat(en_sent_lst) ##'==' removed!
    #en_sent_lst = extract_summary(en_sent_lst)

    if 'zh' not in page_dict.keys(): continue
    zh_page = unicode(page_dict['zh'],'utf-8')
    zh_sent_lst = sent_tokenize(zh_page)
    zh_sent_lst, zh_title_lst = title_struct_feat(zh_sent_lst) ##'==' removed!
    #zh_sent_lst = extract_summary(zh_sent_lst)


    mat = get_score_matrix(zh_sent_lst, en_sent_lst)
    #titlemat = get_title_score_matrix(zh_title_lst, en_title_lst)
    
    f=file('annot/zh_en_'+key.replace(' ','_')+'.txt','w')
    f.write('zh given en:\n')
    for i,sent in enumerate(zh_sent_lst):
        f.write(str(i)+'\t')
        f.write(str(np.argmax(mat[i,:]))+'\t')
        f.write(str(mat[i,:].max())+'\t')
        f.write(sent.encode('utf8')+'\n')
    f.close()

    f=file('annot/en_zh_'+key.replace(' ','_')+'.txt','w')
    f.write('en given zh:\n')
    for i,sent in enumerate(en_sent_lst):
        f.write(str(i)+'\t')
        f.write(str(np.argmax(mat[:,i]))+'\t')
        f.write(str(mat[:,i].max())+'\t')
        f.write(sent.encode('utf8')+'\n')
    f.close()
    print len(zh_sent_lst), len(en_sent_lst)
