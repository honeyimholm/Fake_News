#@brief a new and improved way to scrape the admin start dates
#@author Steffen Holm
from bs4 import BeautifulSoup
import httplib, urllib


conn = httplib.HTTPConnection("www.en.wikipedia.org")

admin_list = ["Adambro"]
admin_start_dict{}
#parse admin application page with beautiful soup
ROOT_HTML = "http://en.wikipedia.org/w/index.php"
for admin in admin_list:
	#construct POST request for the 
	SUBSECTION_POST = "&from="
	params = urllib.urlencode({SUBSECTION_POST: admin[0], "title":"Category:Successful_requests_for_adminship"})
	conn.request("POST", ROOT_HTML, params)
	response = conn.getresponse()
	html = response.read()
	soup = BeautifulSoup(html, 'html.parser')
	#gather all href statements
	print soup.find_all('a')
	#TODO: extract link for given admin name
	#TODO: grab raw html
	#TODO: search for first occurrence of type 02:09 January 13 2006 (UTC)
	#TODO: parse and store
pickle_out = open("blocked_admin_start_dict.pickle","wb")
pickle.dump(admin_start_dict, pickle_out)

