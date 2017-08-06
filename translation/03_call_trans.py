import sys
import os
import pickle
import time
import subprocess
from myconfig import *


corpus = pickle.load(open(catname+'.pkl','rb'))
namelist = corpus.keys()

if os.path.isfile('translated_'+catname+'.pkl'):
    f = open('translated_'+catname+'.pkl','rb')
    corpus2 = pickle.load(f)
    f.close()
else:
    corpus2 = {}

i = 0
for name in namelist:
    if name in corpus2.keys(): continue
    print '===============',name,'==============='
    d = {}
    d['en'] = corpus[name]['en']
    for lang in corpus[name].keys():
        if lang=='en': continue
        tsentlst = []
        print '==========',lang,'=========='
        sentlist = corpus[name][lang].split('\n')
        cmd1 = ('./trans -brief -s '+lang+' -t en ').encode('utf-8')
        for sent in sentlist:
            cmd = cmd1+'\"'+sent.replace('\"','\'')+'\"'
            tsent = subprocess.check_output(cmd, shell=True)
            print tsent
            #print 'origin:', sent
            #print 'translated:', tsent
            tsentlst.append(tsent)
            time.sleep(1)
        d[lang] = ''.join(tsentlst)
    corpus2[name] = d
    f = open('translated_'+catname+'.pkl','wb')
    pickle.dump(corpus2,f)
    f.close()

