#@brief: extracts all talk page comments from a list of users by
#  converting their talk page(s) to xml, then feeding into grawitas for parsing
#@NOTE: this is what a talk page looks like 
#  https://en.wikipedia.org/wiki/User:Antalope
#@NOTE: not all talk pages are formatted the same

#TODO: parse URL to XML
def url2xml(url):
    #try using this https://stackoverflow.com/questions/8908318/looking-for-a-wikipedia-api-that-can-give-me-their-article-in-xml
    pass

#TODO: check if url exists before sending to grawitas
def check_url(url):
    pass

#TODO: use grawitas to parse xml
def grawitas_call(xml):
    pass

#takes in a list of users and returns a dictionary of user, comment_list pairs
def extract_comments(user_list):
    #for now let's keep track of the username, might be helpful later
    comment_dict = {}
    for user in user_list:
        #retreive user base talk page url
        url = "https://en.wikipedia.org/wiki/User_talk:" + user
        url_list = [url]
        #contains all xml for users talk page
        xml_list = []
        #list of comments per user
        comments_list = []
        ARCHIVE_LIMIT = 100
        
        #check for archives
        for num in range(ARCHIVE_LIMIT):
          if(check_url("https://en.wikipedia.org/wiki/User_talk:"+user+"Archive_1")):
            archive = url + "/Archive_" + num
            url_list.append[archive]
          else:
            break
        #parse URL to XML
        for url in url_list:
          xml_list.append(url2xml(url))
        #feed into grawitas
        for xml in xml_list:
          comments_list.append(grawitas_call(xml))
        comment_dict[user] = user_list
    return comment_dict