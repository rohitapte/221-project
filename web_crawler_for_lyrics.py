import urllib2
from bs4 import BeautifulSoup
import time
import re
import itertools
import os.path

print "\n\nSTART"

# loop over the songs and artists that we crawl from metrolyrics website.
url_list = set()
url_list.add("http://www.metrolyrics.com/hey-jude-lyrics-beatles.html")

# SCRAPER
# scrape metro lyrics to get a bunch of sites that we can crawl.
from urlparse import urljoin 

#create list of words to ignore
ignorewords=set(['the','of','to','and','a','in','is','it'])

newpages = set()

#scrape for just the top 100 songs. 
# pages = ["http://www.metrolyrics.com/top100.html", "http://www.metrolyrics.com/top100-alternative.html","http://www.metrolyrics.com/top100-blues.html",\
# "http://www.metrolyrics.com/top100-country.html", "http://www.metrolyrics.com/top100-electronic.html","http://www.metrolyrics.com/top100-hiphop.html",\
# "http://www.metrolyrics.com/top100-indie.html", "http://www.metrolyrics.com/top100-metal.html","http://www.metrolyrics.com/top100-pop.html",\
# "http://www.metrolyrics.com/top100-punk.html","http://www.metrolyrics.com/top100-rock.html"]

# for page in pages:
# 	try: 
# 		c = urllib2.urlopen(page)
# 	except: 
# 		print "Could not open %s" % page
# 		continue 
# 	soup = BeautifulSoup(c.read())
# 	links = soup('a')
# 	for link in links: 	
# 		if ('href' in dict(link.attrs)):
# 			url = link['href']
# 			# add to list only if the last 5 chars are .html and it not top100 link
# 			taboo_list=["http://www.metrolyrics.com/videos.html","http://www.metrolyrics.com/news.html","http://www.metrolyrics.com/top-artists.html","http://www.metrolyrics.com/rolling-stone-top500.html","http://metrolyrics.com/add.html"]
# 			if url[-5:] == ".html" and url[:33]!="http://www.metrolyrics.com/top100" and url not in taboo_list:
# 				# add to the list 
# 				url_list.add(url)

# Scrape for artist specific sites - self-defined artists to start with.
# artist_pages = (("miley cyrus","http://www.metrolyrics.com/miley-cyrus-lyrics.html"),("justin timberlake","http://www.metrolyrics.com/justin-timberlake-lyrics.html"),\
# 	("coldplay","http://www.metrolyrics.com/coldplay-lyrics.html"),("lana del rey","http://www.metrolyrics.com/lana-del-rey-lyrics.html"),\
# 	("bruno mars","http://www.metrolyrics.com/bruno-mars-lyrics.html"),("jay-z","http://www.metrolyrics.com/jay-z-lyrics.html"),\
# 	("one direction","http://www.metrolyrics.com/"))

# Add tuples to the artist_pages array.
top_dir = "http://www.metrolyrics.com/top-artists.html"

res = urllib2.urlopen(top_dir)
html_code = res.read()
bs_obj = BeautifulSoup(html_code)
page_links = []
# print [(' '.join(a.get('href').split('http://www.metrolyrics.com/')[1].split('-lyrics.html')[0].split('-')), a.get('href')) for a in bs_obj.findAll('a')]
try :
	print "trying to get all links"
	page_links = itertools.ifilter(lambda x: 'http://' in x[1], [(' '.join(a.get('href').split('http://www.metrolyrics.com/')[1].split('-lyrics.html')[0].split('-')), a.get('href')) for a in bs_obj.findAll('a')])
except Exception: # Magnificent exception handling
    pass
artist_pages = []
for link_tuple in page_links: 
	if '-lyrics.html' in link_tuple[1]: 
		artist_pages.append((link_tuple[0],link_tuple[1]))

# Using the artist_pages we now run through each one and find all of the lyrics from that artist
# Extract each song lyrics url and populate url_lists 
directory = "lyrics/"
names_list = []
for k,v in artist_pages: 
	try: 
		c = urllib2.urlopen(v)
	except: 
		print "Could not open %s" % v
		continue
	soup = BeautifulSoup(c.read())
	links = soup('a')
	for link in links: 	
		if ('href' in dict(link.attrs)):
			url = link['href']
			# add to list only if the last 5 chars are .html and it not top100 link
			taboo_list=["http://www.metrolyrics.com/videos.html","http://www.metrolyrics.com/news.html","http://www.metrolyrics.com/top-artists.html","http://www.metrolyrics.com/rolling-stone-top500.html","http://metrolyrics.com/add.html"]
			if url[-5:] == ".html" and url[:33]!="http://www.metrolyrics.com/top100" and url not in taboo_list:
				# add to the list 
				url_list.add(url)
				names_list.append(k)
print len(url_list)

# Run through each song lyric and write to files
for url in url_list:
	# Check if the file exists - if not, then continue
	filename = (url.split("http://www.metrolyrics.com/")[1].split(".html"))[0] + ".txt"
	filepath1 = "lyrics/" + filename
	filepath2 = "lyrics/artist/" + filename
	if not (os.path.exists(filepath1) or os.path.exists(filepath2)): 
		print "adding one file or song: " + filename
		file = open(filepath2, 'w')

		request = urllib2.Request(url)
		response = urllib2.urlopen(request)
		soup = BeautifulSoup(response)

		#Get artist
		artist_string = soup.find(text=re.compile('artist'))     
		if artist_string != None:   
			start = artist_string.find('\"artist\":')
			artist_string = artist_string[start+10:]
			end = artist_string.find('\"')
			artist_string = artist_string[:end]
			file.write(artist_string.encode('utf-8'))
			file.write('\n')

			#Get genre
			genre_string = soup.find(text=re.compile('tag='))
			if genre_string !=None: 
				start = genre_string.find('tag=');
				genre_string = genre_string[start+4:]
				end = genre_string.find(';')
				genre_string = genre_string[:end]
				file.write(genre_string.encode('utf-8'))
				file.write('\n')

				#Get lyrics        
				p_tags = soup.find_all('p')
				for i, child in enumerate(p_tags):
					if len(child.attrs) > 0:
						if child.has_attr('class')==True:
							if child.attrs['class'][0].find(u'verse') == 0:
								for string in child.stripped_strings:
									file.write(string.encode('utf-8'))
									file.write('\n')

print "done"