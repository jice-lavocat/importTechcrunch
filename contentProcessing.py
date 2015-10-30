import re
import os
import urllib
from translate import translator
import lxml.html
import requests
from lxml import etree
from datetime import datetime
import urlparse
import goslate
import time
import random

def getOpener():
	""" 
	Return fake user agent
	"""
	import urllib2
	opener = urllib2.build_opener()
	headers = [{'User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'},
	{'User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6'},
	{'User-Agent','Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0; Touch)'},
	{'User-Agent','Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'},
	{'User-Agent','Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:38.0) Gecko/20100101 Firefox/38.0'},
	{'User-Agent','Mozilla/5.0 ;Windows NT 6.1; WOW64; Trident/7.0; rv:11.0; like Gecko'},
	{'User-Agent','Mozilla/5.0 ;Windows NT 6.2; WOW64; rv:27.0; Gecko/20100101 Firefox/27.0'},
	{'User-Agent','Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 Safari/534.3'}]
	#,	{'User-agent', 'Mozilla/5.0'}]
	header = random.choice(headers)
	print "Using header : %s" % header
	opener.addheaders = [header]
	return opener


def html2flat(html):
	""" Takes html and return clean html where :
			* <a> have been removed
	"""

	cleanHtml = html
	cleanHtml = re.sub('</?[div|a|iframe^>]*>', '', cleanHtml)

	return cleanHtml

def going2Sleep():
	randi = random.randint(25,50)
	print "Going to sleep for %s seconds" % randi
	time.sleep(randi)
	return None


def translateStr(string):
	opener = getOpener()
	gs = goslate.Goslate(opener = opener, debug=True)
	going2Sleep()
	result= gs.translate(string, 'fr', source_language='en')
	# return translator('en', 'fr', string)[0][0][0]
	return result

def translateHtml(html):
	"""
	Translate EN html to FR html via Google Translapte api
	We split the text for each paragraph and block of text
	Each blob is stored in a list, and the html is re-written with replacement elements
	So <p>lorem ipsum</p><p>blabla orum</p> becomes <p>{{--1--}}</p><p>{{--2--}}</p>
	Then, translate is given the list of blobs : translate(list_text, "fr")
	The resulting list is used to replace {{--xx--}} in the original html
	"""

	contentParsed = lxml.html.fromstring(html)
	contentTranslated = ""
	replaceId = 0
	textList = []
	opener = getOpener()
	gs = goslate.Goslate(opener = opener, debug=True)

	# Extract the paragraphs and headings to translate them in batch
	for ind, elem in enumerate(contentParsed):
		#if elem.tag in ["p", "blockquote", "span"]
		if elem.tag in ["p", "h1", "h2", "h3", "h4", "h5", "blockquote"]: # if tag contains text
			currentParagraph = etree.tostring(elem)
			cleanedParagraph = re.sub('<[^>]*>', '', currentParagraph) # we remove all tags from the current element
			textList.append(cleanedParagraph) # we had the raw text to the list that will be tranlated

			#translatedPara = translator('en', 'fr', cleanedParagraph)
			#if not isinstance(translatedPara[0], int):
			#	# returnedPara = "<" + elem.tag +">"+(translatedPara[0][0][0]).encode('ascii', 'xmlcharrefreplace')+"</" + elem.tag +">"
			returnedPara = "<" + elem.tag +">{{--"+ str(replaceId) +"--}}</" + elem.tag +">"
			contentTranslated += returnedPara
			replaceId += 1
		else:
			if not (elem.tag=="img" and ind==0): #we remove the first picture (already took it via goose)
				print str(elem.tag) + " : " + str(ind)
				contentTranslated += etree.tostring(elem) #add the element without further process

	# Translate the paragraphs
	going2Sleep()
	if textList != []:
		transState = gs.translate(textList, 'fr', source_language='en')
		translatedBlobs = list(transState)

	if len(translatedBlobs) != len(textList):
		raise Exception("Problem during translation - we got a different number of paragraph fromthe translation")

	print "translated blobs :"
	print translatedBlobs

	for elem in translatedBlobs: #we should have the same number of translations than the replacement patterns
		print "We should replace element :"
		print translatedBlobs.index(elem)
		ind = translatedBlobs.index(elem)
		replacementPattern = "{{--" + str(ind) + "--}}"
		print "replacement pattern is : "
		print replacementPattern
		contentTranslated = re.sub(replacementPattern, elem, contentTranslated)
		print "="*5
		print contentTranslated

	return contentTranslated

def getFrenchSlug(article):
	""" 
	From an article, returns the Frehcn slug
	Here, "published_time is a datetime
	"""
	# only alphanumeric
	titre = re.sub(r'\W+', ' ', article["titre"].encode('ascii','ignore')) # only alphanumeric
	slug = article["published_time"].strftime('%Y-%m-%d')+"_"+"-".join(titre.split())
	slug = slug.lower() # lowercase
	slug = re.sub("-+", "-", slug) # Replace several dashes by only one dash
	return slug

def string2Slug(s):
	# only alphanumeric
	s = re.sub(r'\W+', ' ', s.encode('ascii','ignore')) # only alphanumeric
	s = s.lower() # lowercase
	s = re.sub(" +", "-", s) # Replace several dashes by only one dash
	s = re.sub("-+", "-", s) # Replace several dashes by only one dash
	return s

def getAuthorNameTechCrunch(html):
	"""
	From a techcrunch article, extracts the author name
	"""
	contentParsed = lxml.html.fromstring(html)
	authorName = contentParsed.xpath('//a[@rel="author"]/text()')[0]
	authorSlug = string2Slug(authorName)
	authorUrl = contentParsed.xpath('//a[@rel="author"]//@href')[0]
	if authorUrl[0]=="/":
		authorUrl = "http://techcrunch.com" + authorUrl
	author = {"name": authorName, "slug": authorSlug, "url": authorUrl}
	return author

def importAuthor(author):
	"""
	Import data for author=author
	"""
	authorHtml = (requests.get(author["url"])).text
	contentParsed = lxml.html.fromstring(authorHtml)
	authorJson = {}

	description = contentParsed.xpath("//div[@class='profile-text text']/p/text()")
	finalDescription = ""
	for sentence in description:
		if "techcrunch" not in sentence.lower():
			finalDescription += sentence

	authorJson["description"] = finalDescription
	try:
		authorTwitter = contentParsed.xpath("//div[@class='profile cf']//a[contains(@href, 'twitter')]/@href")[0]
	except:
		authorTwitter = None
	authorJson["twitter"] = authorTwitter
	try:
		authorLinkedin = contentParsed.xpath("//div[@class='profile cf']//a[contains(@href, 'linkedin')]/@href")[0]
	except:
		authorLinkedin = None
	authorJson["linkedin"] = authorLinkedin
	if finalDescription!= "":
		authorJson["frenchDescription"] = translateStr(finalDescription)
	else:
		authorJson["frenchDescription"] = ""
	return authorJson

def data2Hugo(article, fileFolder):
	"""
	Uses the metadata to create a valid Hugo file
	"""
	from main import mkdir_p
	filename = os.path.join(fileFolder, article["slug"] + ".md")
	with open(filename, 'w') as outfile:

		# Metadata
		outfile.write("---\n")
		
		#Titre
		if "titre" in article:
			outfile.write('title: ' + article["titre"].encode('utf-8') +"\n")
		else:
			outfile.write('title: ' + article["title"].encode('utf-8') +"\n")
		
		#Layout
		outfile.write("layout: post\n")

		#Tags
		tagsHugo = "['" + "','".join(article["tags"]) + "']"
		outfile.write( ("tags: " + tagsHugo + "\n").encode('ascii', 'ignore')  )
 
		#Date
		#humanDate = datetime.fromtimestamp(int(article["published_time"])/1000.0)
		if isinstance(article["published_time"], datetime):
			humanDate = article["published_time"]
		else:
			humanDate = datetime.fromtimestamp((article["published_time"])/1000.0)
		humanDate = humanDate.strftime('%Y-%m-%d')
		outfile.write("date: " + humanDate + "\n")

		# Categories
		outfile.write("categories: [actualites] \n")

		# Thumbnail
		if "thumbnail" in article:
			thumbnail = article["thumbnail"]
			thumbPath = os.path.join(fileFolder, "thumbnails")
			mkdir_p(thumbPath)

			path = urlparse.urlparse(thumbnail).path
			ext = os.path.splitext(path)[1]
			thumbFilename = os.path.join(thumbPath, article["frenchSlug"] + ext)

			#urllib.urlretrieve(thumbnail,thumbFolder)
			if not os.path.isfile(thumbFilename): # !if image does not exist yet
				with open(thumbFilename, 'wb') as thumbfile:
					thumbfile.write(urllib.urlopen(thumbnail).read())
				print "Image saved under " + unicode(thumbPath)

			# thumbnails in /images/thumbs/
			thumbStaticFilePath = os.path.join("images", "thumbnails",  article["frenchSlug"] + ext)
			outfile.write("thumbnail: /" + thumbStaticFilePath +"\n")

		#Teaser image
		imgTeaser = article["images"][0]
		path = urlparse.urlparse(imgTeaser).path
		ext = os.path.splitext(path)[1]

		teaserPath = os.path.join(fileFolder, "teaser")	
		mkdir_p(teaserPath)	
		teaserFilename = os.path.join(teaserPath, article["frenchSlug"] + ext)
		if not os.path.isfile(teaserFilename): # !if image does not exist yet
				with open(teaserFilename, 'wb') as imgFile:
					imgFile.write(urllib.urlopen(imgTeaser).read())
				print "Image saved under " + unicode(imgTeaser)

		# thumbnails in /images/thumbs/
		teaserStaticFilePath = os.path.join("images", "teaser",  article["frenchSlug"] + ext)
		outfile.write("teaserImage: /" + teaserStaticFilePath +"\n")

		# Images


		outfile.write("---\n\n")
		outfile.write(article["goose"]["frenchContent"].encode('ascii', 'xmlcharrefreplace'))