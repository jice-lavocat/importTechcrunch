import re
import os
import urllib
from translate import translator
import lxml.html
from lxml import etree
from datetime import datetime
import urlparse

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
	for ind, elem in enumerate(contentParsed):
		#if elem.tag in ["p", "blockquote", "span"]
		if elem.tag in ["p", "h1", "h2", "h3", "h4", "h5", "blockquote"]:
			currentParagraph = etree.tostring(elem)
			cleanedParagraph = re.sub('<[^>]*>', '', currentParagraph) #we remove all tags
			translatedPara = translator('en', 'fr', cleanedParagraph)
			if not isinstance(translatedPara[0], int):
				returnedPara = "<" + elem.tag +">"+(translatedPara[0][0][0]).encode('ascii', 'xmlcharrefreplace')+"</" + elem.tag +">"
				contentTranslated += returnedPara
		else:
			if not (elem.tag=="img" and ind==0):
				print str(elem.tag) + " : " + str(ind)
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
		if "titre" in article:
			outfile.write('title: ' + article["titre"].encode('utf-8') +"\n")
		else:
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