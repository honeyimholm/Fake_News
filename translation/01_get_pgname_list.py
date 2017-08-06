import sys
from myconfig import *
from util_wikiapi import *

pgnamelist = []
crawl_pgname('Category:'+catname,pgnamelist=pgnamelist)
f = file(catname+'.txt','w')
for pgname in pgnamelist: f.write(to_utf8(pgname)+'\n')
f.close()
