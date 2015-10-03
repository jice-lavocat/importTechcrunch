import re
import os
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

def data2Hugo(article, fileFolder):
	"""
	Uses the metadata to create a valid Hugo file
	"""
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
		humanDate = datetime.fromtimestamp(int(article["published_time"])/1000.0)
		humanDate = humanDate.strftime('%Y-%m-%d')
		outfile.write("date: " + humanDate + "\n")

		# Categories
		outfile.write("categories: [actualites] \n")

		outfile.write("---\n\n")
		outfile.write("jice")