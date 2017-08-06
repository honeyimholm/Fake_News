import sys
from text_aligner import *
import pickle
import nltk
from scipy.optimize import linear_sum_assignment

def str2utf8(s): return unicode(s,'utf-8')

f = file('translated_corpus.pkl','rb')
corpus = pickle.load(f)
corpus.pop('Donald Trump')
f.close()

for key in corpus.keys():
    page_dict = corpus[key]
    en_page = unicode(page_dict['en'],'utf-8')
    key = unicode(key,'utf-8')
    print key
    #en_sent_lst = nltk.sent_tokenize(en_page)
    en_sent_lst = sent_tokenize(en_page)
    en_sent_lst, en_title_lst = title_struct_feat(en_sent_lst) ##'==' removed!

    if 'zh' not in page_dict.keys(): continue
    zh_page = unicode(page_dict['zh'],'utf-8')
    #zh_sent_lst = nltk.sent_tokenize(zh_page)
    zh_sent_lst = sent_tokenize(zh_page)
    zh_sent_lst, zh_title_lst = title_struct_feat(zh_sent_lst) ##'==' removed!
    mat = get_score_matrix(zh_sent_lst, en_sent_lst)
    titlemat = get_title_score_matrix(zh_title_lst, en_title_lst)
    matches = linear_sum_assignment(-mat)
    

    para_pos_lst = paragraph_align(zh_sent_lst, zh_title_lst, en_sent_lst, en_title_lst)
    f = file('align/para_'+key.replace(' ','_')+'.txt','w')
    para_match_print(para_pos_lst, zh_sent_lst, zh_title_lst, en_sent_lst, en_title_lst,f)
    f.close()

    """
    f = file('align/sent_'+key.replace(' ','_')+'.txt','w')
    match_print(zh_sent_lst, en_sent_lst, matches, mat, f)
    f.close()

    f = file('translated/en_'+key.replace(' ','_')+'.txt','w')
    print_pages(en_sent_lst,en_title_lst,f)
    f.close()
    f = file('translated/zh_'+key.replace(' ','_')+'.txt','w')
    print_pages(zh_sent_lst,zh_title_lst,f)
    f.close()
    """
