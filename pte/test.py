import sys
import pickle

testslt = ['Akio Toyoda']
f = file('translated_corpus.pkl','rb')
corpus = pickle.load(f)
f.close()

for key in testlst:
    
