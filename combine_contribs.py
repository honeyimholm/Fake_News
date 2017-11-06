#@brief: script to combine pickled_contribs
from os import listdir
from os.path import isfile, join
import pickle

mypath = "pickled_blocked_contribs/"
file_list = [f for f in listdir(mypath) if isfile(join(mypath, f))]
print file_list
combined_dict = {}
for f in file_list:
	print "handling " + f
	pickle_in = open(mypath+f,"rb")
	try:
		admin_start_dict = pickle.load(pickle_in)
	except: 
		print "FAILED for file " + f
		continue
	admin_name = f[:f.index('_')]
	combined_dict[admin_name] = admin_start_dict
pickle_out = open("combined_contribs_dict.pickle","wb")
pickle.dump(combined_dict, pickle_out)
