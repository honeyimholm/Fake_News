import re

text = ""
title_pattern = re.compile(r'\'(.+?)\',')
with open('C:\Users\sahol\Desktop\Fake News Deep Learning\wiki\\enwiki-latest-category - Copy.txt', 'r') as myfile:
    text=myfile.read().replace('\n', '')
f = open('C:\Users\sahol\Desktop\Fake News Deep Learning\wiki\\formatted_categories.txt', 'w')
text = text.replace('\\\'',"",10000000)
f.write(text)
f.close() 
out_file = open('C:\Users\sahol\Desktop\Fake News Deep Learning\wiki\\category_list.txt','w')
for title in re.findall(title_pattern, text):
	out_file.write(title+"\n")
	print title
out_file.close()
myfile.close()