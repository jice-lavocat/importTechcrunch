import re
import os
import urllib
from translate import translator
import lxml.html
from lxml import etree
from datetime import datetime

def html2flat(html):
	""" Takes html and return clean html where :
			* <a> have been removed
	"""

	cleanHtml = html
	cleanHtml = re.sub('</?[div|a|iframe^>]*>', '', cleanHtml)

	return cleanHtml

def translateStr(string):
	return translator('en', 'fr', string)[0][0][0]

def translateHtml(html):
	"""
	Translate EN html to FR html via Google Translapte api
	"""
	contentParsed = lxml.html.fromstring(html)
	contentTranslated = ""
	for elem in contentParsed:
		#if elem.tag in ["p", "blockquote", "span"]
		if elem.tag in ["p", "h1", "h2", "h3", "h4", "h5", "blockquote"]:
			currentParagraph = etree.tostring(elem)
			cleanedParagraph = re.sub('<[^>]*>', '', currentParagraph) #we remove all tags
			translatedPara = translator('en', 'fr', cleanedParagraph)
			if not isinstance(translatedPara[0], int):
				returnedPara = "<" + elem.tag +">"+translatedPara[0][0][0]+"</" + elem.tag +">"
				contentTranslated += returnedPara
		else:
			contentTranslated += etree.tostring(elem)
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
		outfile.write('title: ' + article["title"].encode('utf-8') +"\n")
		
		#Layout
		outfile.write("layout: post\n")

		#Tags
		tagsHugo = "['" + "','".join(article["tags"]) + "']"
		outfile.write("tags: " + tagsHugo + "\n")
 
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
			thumbFilename = os.path.join(thumbPath, article["slug"] + ".jpg")
			thumbFilenameNoExt = os.path.join(fileFolder, "thumbnails", article["slug"])
			thumbFolder = os.path.join(fileFolder, "thumbnails")
			#urllib.urlretrieve(thumbnail,thumbFolder)
			with open(thumbFilename, 'wb') as thumbfile:
				thumbfile.write(urllib.urlopen(thumbnail).read())
			print "Image saved under " + str(thumbPath)

		outfile.write("---\n\n")
		outfile.write("jice")