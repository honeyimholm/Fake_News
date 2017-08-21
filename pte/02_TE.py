"""
Text Entailment experiment
"""
import sys
sys.path.append('/home/harry/github/PyAI/util/')
from util_ml import *
from text_aligner import *
from sklearn.metrics import accuracy_score, f1_score
import numpy as np
from sklearn.svm import SVC

article_list = ['Korean_War','Bob_Iger','Aliko_Dangote','Tim_Cook']
l1,l2 = 'en','zh'

def ent_feats(sent_feats,para_feats):
    sent_ents = sent_feats['en']
    para_ents = para_feats['en']
    se_num, pe_num = len(sent_ents),len(para_ents)
    sim_matrix = np.zeros((se_num,pe_num))
    for i,s_ent in enumerate(sent_ents):
        for j,p_ent in enumerate(para_ents):
            sim_matrix[i,j] = entity_sim(s_ent, p_ent)
    sim = np.max(sim_matrix, axis=1)
    #print sim
    #return [np.max(sim), np.min(sim), len(sent_ents), np.sum(sim>0.3)]
    return [np.min(sim)]

def non_stop_feat(featdict,featdict_lst):
    ns_unigram = featdict['nonstop']
    ref_ns_unigrams = [fdict['nonstop'] for fdict in featdict_lst]
    mat = np.zeros(len(featdict_lst))
    for i,unigram in enumerate(ref_ns_unigrams):
        mat[i] = item_match_score(unigram, ns_unigram)
    return np.max(mat)
    

featlst = []
lablst = []
for article in article_list:
    fn1 = 'annot/'+l1+'_'+l2+'_'+article+'.txt'
    sentlst = [l.split('\t')[-1] for l in file(fn1)]
    sentlst = [unicode(s, 'utf-8') for s in sentlst]
    ref_fdict_lst = extract_all_feature(sentlst)

    ref_para = u' '.join(sentlst)
    para_feat = extract_all_feature([ref_para])[0]

    fn2 = 'annot/'+l2+'_'+l1+'_'+article+'.txt'
    for l in file(fn2):
        if l[0]=='T' or l[0]=='F':
            ngram_score = float(l.split('\t')[2])
            sfeat = extract_all_feature([unicode(l,'utf-8')])[0]
            ### extract other features
            ## sent + para
            ent_feat_lst = ent_feats(sfeat, para_feat)
            #one_time_ent = 
            ## sent+ sentlst
            nonstop_unigram = non_stop_feat(sfeat,ref_fdict_lst)
            lab = l[0]
            lablst.append(lab)
            featlst.append([ngram_score,nonstop_unigram]+ent_feat_lst)

    sentlst = [l.split('\t')[-1] for l in file(fn2)]
    sentlst = [unicode(s, 'utf-8') for s in sentlst]
    ref_fdict_lst = extract_all_feature(sentlst)
    ref_para = u' '.join(sentlst)
    para_feat = extract_all_feature([ref_para])[0]
    for l in file(fn1):
        if l[0]=='T' or l[0]=='F':
            ngram_score = float(l.split('\t')[2])
            sfeat = extract_all_feature([unicode(l,'utf-8')])[0]
            ### extract other features
            ## sent + para
            ent_feat_lst = ent_feats(sfeat, para_feat)
            #one_time_ent = 
            ## sent+ sentlst
            nonstop_unigram = non_stop_feat(sfeat,ref_fdict_lst)
            lab = l[0]
            lablst.append(lab)
            featlst.append([ngram_score,nonstop_unigram]+ent_feat_lst)

X = np.array(featlst)
y = np.array(lablst)
ypred_total, ytest_total = [],[]
for Xtrain, ytrain, Xtest, ytest in KFold(X,y):
    svc = SVC(C=100,kernel='linear')
    svc.fit(Xtrain,ytrain)
    ypred = svc.predict(Xtest)
    ypred_total+=ypred.tolist()
    ytest_total+=ytest.tolist()
print accuracy_score(ytest_total, ypred_total)
"""
predlst = []
thres = 0.28
for feat in featlst:
    if feat>thres: predlst.append('T')
    else: predlst.append('F')
acc = accuracy_score(lablst,predlst)
lablst = np.array(lablst)=='T'
predlst = np.array(predlst)=='T'
f1 = f1_score(lablst,predlst)
print acc,f1
print predlst
"""
