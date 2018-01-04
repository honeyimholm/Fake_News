import re
import pickle

#@brief: takes in raw admin start date file
#assumes has been scraped from https://en.wikipedia.org/wiki/User:NoSeptember/List_of_Administrators
#with format "name (...) date_start date_joined

remove_alpha_index_regex = "[A-Z]\[edit\]"
#capture groups of name, year, month, day promoted to admin 
#sometimes day is omitted, sometimes gives year again
#we'll pick first two digits of the year (19 or 20)
#if both are omitted we'll deal with that
capture_name_date_regex =  "(.*) \(t.*\) (\d*)? ?(\w*)? ?(\d{0,2})"
OUTPUT_FILE = "admin_start_dict.pickle"

admin_contrib_dict = {}
with open("admin_start_list_raw.txt") as f:
    for line in f:
        if(re.search(remove_alpha_index_regex, line)):
        	continue
    	name_date = re.findall(capture_name_date_regex, line)
    	if(name_date):
			print("parsing: " + line)
			#default tuple is immutable
			name_date = list(name_date[0])
			print(name_date)
			if(name_date[1]==''):
				#without year data point is useless
				continue
			#deal with missing data
			if(name_date[2]==''):
				name_date[2] = 'Jan'
			if(name_date[3]==''):
				name_date[3] = '1'
			admin_contrib_dict[name_date[0]] = [i for i in name_date[1:]]
print(admin_contrib_dict)
print("pickling!")
pickle_out = open(OUTPUT_FILE,"wb")
pickle.dump(admin_contrib_dict, pickle_out)
pickle_out.close()