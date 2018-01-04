import sys
sys.path.append('/home/harry/github/PyAI/nlp/util')
from util_nlp import *
import nltk
import numpy as np
from scipy.optimize import linear_sum_assignment
import spacy

nlp = spacy.load('en')


def sent_tokenize(doc):
    lst = doc.split('\n')
    sentlst = []
    for s in lst:
        if len(s)>50: sentlst+=nltk.sent_tokenize(s)
        elif len(s)>3: sentlst.append(s)
    return sentlst

####################################
## Feature extraction
####################################

def get_spacy_nlp_dict(titlelst):
    docdict = {}
    for title in titlelst:
        if title not in docdict:
            docdict[title] = nlp(title)
    return docdict
    

def title_struct_feat(sentlst):
    topic_stack = ['Summary']
    depth_stack = ['10']
    title_feat_lst = []
    pure_sentlst = []
    for sent in sentlst:
        if '==' in sent:
            depth = sent.index(' ')
            while len(depth_stack)>0 and depth_stack[-1]>=depth:
                topic_stack.pop(-1)
                depth_stack.pop(-1)
            topic_stack.append(sent.replace('=',''))
            depth_stack.append(depth)
        else:
            title_feat_lst.append(str.join(' ',topic_stack))
            pure_sentlst.append(sent)
    return pure_sentlst, title_feat_lst

def add_spacy_features(sent,feat_dict={}):
    doc = nlp(sent)
    feat_dict['en'] = doc.ents
    feat_dict['w2v'] = np.array([t.vector for t in doc])
    feat_dict['nonstop'] = [t for t in doc if not t.is_stop]

def extract_ngrams(sent):
    tokens = tokenization(sent)
    lemmatizer = getLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    ngrams = ngramStrExtract(tokens,1)+ngramStrExtract(tokens,2)+ngramStrExtract(tokens,3)
    return ngrams

def extract_all_feature(sentlst):
    feat_dict_lst = []
    for sent in sentlst:
        feat_dict = {}
        feat_dict['ngram'] = extract_ngrams(sent)
        add_spacy_features(sent, feat_dict=feat_dict)
        feat_dict_lst.append(feat_dict)
    return feat_dict_lst

######################################
## matching scores
######################################
def w2v_avg_score(doc1,doc2):
    v1,v2 = doc1.vector, doc2.vector
    return np.dot(v1,v2)/np.sqrt(v1.dot(v1)*v2.dot(v2))
    #return np.sqrt((v1-v2)**2)

def item_match_score(lst1,lst2):
    match = float(0)
    for ng1 in lst1:
        for ng2 in lst2:
            if ng1==ng2:
                match+=1
                break
    #match/=max(len(nglst2),len(nglst1))
    match/=(len(lst2)+len(lst1))/2
    return match

def ngram_match_score(feat_dict1,feat_dict2):
    nglst1,nglst2 = feat_dict1['ngram'], feat_dict2['ngram']
    return item_match_score(nglst1,nglst2)

def nonstop_unigram_match(feat_dict1,feat_dict2):
    lst1,lst2 = feat_dict1['nonstop'], feat_dict2['nonstop']
    return item_match_score(lst1,lst2)

######################################
## Alignment
######################################

def get_score_matrix(sentlst1, sentlst2):
    featdicts1 = extract_all_feature(sentlst1)
    featdicts2 = extract_all_feature(sentlst2)
    
    mat = np.zeros((len(sentlst1),len(sentlst2)))
    for i in range(len(sentlst1)):
        for j in range(len(sentlst2)):
            #mat[i,j] = nonstop_unigram_match(featdicts1[i],featdicts2[j]) \
            #        + ngram_match_score(featdicts1[i],featdicts2[j])
            mat[i,j] = ngram_match_score(featdicts1[i],featdicts2[j])
    return mat

def get_title_score_matrix(title_feat1,title_feat2):
    mat = np.zeros((len(title_feat1),len(title_feat2)))
    docd1, docd2 = get_spacy_nlp_dict(title_feat1), get_spacy_nlp_dict(title_feat2)
    for i in range(len(title_feat1)):
        for j in range(len(title_feat2)):
            v1 = docd1[title_feat1[i]]
            v2 = docd2[title_feat2[j]]
            mat[i,j] = w2v_avg_score(v1,v2)
            #titlelst1 = title_feat1[i].split()
            #titlelst2 = title_feat2[j].split()
            #mat[i,j] = item_match_score(titlelst1,titlelst2)
    return mat

######################################
## Match Analysis
######################################

def match_scores_stat(score_mat,matches):
    m1,m2 = matches[0], matches[1]
    scorelst = [score_mat[i,j] for i,j in zip(m1,m2)]
    return np.mean(scorelst), np.var(scorelst)

def match_print(sentlst1, sentlst2, matches, score_mat, f):
    for i,sent in enumerate(sentlst1):
        out = '[origin]: '+sent
        if i in matches[0]:
            j = matches[0].tolist().index(i)
            j = matches[1][j]
            out+='\n[aligned]:'+sentlst2[j]
            out+='\n score: '+str(score_mat[i][j])
        out+='\n\n'
        f.write(out.encode('utf8'))
        
def print_pages(sentlst,titlelst,f):
    lasttitle = ''
    for sent, title in zip(sentlst,titlelst):
        out = ''
        if title!=lasttitle:
            out = '\n=='+title+'\n'
            lasttitle = title
        out+=sent+'\n'
        f.write(out.encode('utf8'))

######################################
## Paragraph Alignment
####################################a#

def find_align_block(score_matrix):
    para_size, page_size = score_matrix.shape
    if page_size<para_size/2+1: return []
    maxscore = 0
    r = (-1,-1)
    for i in range(page_size):
        for j in range(i+para_size/2, i+para_size*2):
            if j>page_size: break
            mat = score_matrix[:,i:j]
            matches = linear_sum_assignment(-mat)
            score = np.sum([mat[k,l] for k,l in zip(matches[0],matches[1])])
            if maxscore<score: 
                maxscore = score
                r =(i,j)
    print(r)
    return r

def list_remove_dup(lst):
    lst2 = []
    for l in lst:
        if l not in lst2: lst2.append(l)
    return lst2

def paragraph_align(sentlst1,titlelst1,sentlst2,titlelst2):
    score_matrix =  get_score_matrix(sentlst1,sentlst2)
    para_pos_lst = []
    titlesetlst = list_remove_dup(titlelst1)
    for title in titlesetlst:
        idxlst = [i for i in range(len(titlelst1)) if titlelst1[i]==title]
        idxs = np.array(idxlst)
        mat = score_matrix[idxs,:]
        start,end = find_align_block(mat)
        para_pos_lst.append((idxs[0],idxs[-1],start,end))
    return para_pos_lst

def para_match_print(para_pos_lst,sentlst1,titlelst1,sentlst2,titlelst2,f):
    for pos in para_pos_lst:
        ori_start, ori_end, align_start, align_end = pos
        out = '[origin]: \n=='+titlelst1[ori_start]+'==\n'
        out+=str.join('\n', sentlst1[ori_start:ori_end+1])
        if align_start>0:
            out+='\n[align]: \n'+str.join('\n', sentlst2[align_start:align_end+1])+'\n\n'
        else:
            out+='\n[not aligned]\n\n'
        f.write(out.encode('utf8'))
