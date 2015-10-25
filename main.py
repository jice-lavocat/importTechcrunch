from feedData import feed2data
import contentProcessing
import json
import os, errno
import datetime
from goose import Goose
import requests

""" Utils """
""""""""""""""

def mkdir_p(path):
    """
    Make new dir if not exist
    """
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def dumpInFile(path, jsonData):
	""" 
	Dump json in a file 
	"""
	indent = 3
	with open(path, 'w') as outfile:
	    json.dump(jsonData, outfile, indent=indent, default=default)
	    print unicode(path) + " : created"

def default(obj):
    """Default JSON serializer."""
    # see http://stackoverflow.com/a/15823348
    import calendar, datetime

    if isinstance(obj, datetime.datetime):
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()
    millis = int(
        calendar.timegm(obj.timetuple()) * 1000 +
        obj.microsecond / 1000
    )
    return millis


""" Main script """
""""""""""""""""""""

urlTechcrunch = "http://feeds.feedburner.com/techcrunch/startups?format=xml"
data = feed2data(urlTechcrunch)

# Save meta data to file
mkdir_p(os.path.join(".", "data"))
metaDataPath = os.path.join(".", "data", "metadata")
articlePath = os.path.join(".", "data", "articles")
authorPath = os.path.join(".", "data", "authors")
#savePath = os.path.join(".", "data", "hugo")
mkdir_p(metaDataPath)
mkdir_p(articlePath)
mkdir_p(authorPath)
#mkdir_p(savePath)

# We keep only one file per hour
fileName = data["last_update"].strftime("%Y-%m-%d_%H") + ".json"
filePath = os.path.join(metaDataPath, fileName)

dumpInFile(filePath, data)

for article in data["items"]:
	fileName = article["slug"] + ".json"
	fileFolder = os.path.join(articlePath, article["slug"])
	mkdir_p(fileFolder) 

	filePath = os.path.join(fileFolder, fileName)
	# Add file if not existing yet
	if not os.path.isfile(filePath):
		print "Going Goose"
		# import the article via Goose
		raw_html = (requests.get(article["link"])).text
		# g = Goose()
		# art = g.extract(raw_html=raw_html)

		# flatContent = contentProcessing.html2flat(art.content_html.decode('ascii', 'ignore'))
		# frenchContent = contentProcessing.translateHtml(flatContent)
		# goose = {"title" : art.title, "content": art.content_html, "flatContent" : flatContent, "frenchContent": frenchContent}

		# article["goose"] = goose

		# # French Element
		# frenchTitle = contentProcessing.translateStr(article["title"])
		# article["titre"] = frenchTitle
		# # Slug 
		# article["frenchSlug"] = contentProcessing.getFrenchSlug(article)

		# Extract author
		author = contentProcessing.getAuthorNameTechCrunch(raw_html)
		article["author"] = author
		print author

		# Let's import the author if we don't have it
		fileAuthor = os.path.join(authorPath, author["slug"] + ".json")
		if not os.path.isfile(fileAuthor):
			authorJson = contentProcessing.importAuthor(author)
			print authorJson
			# dumpInFile(fileAuthor, authorJson)


		# # Save data
		# dumpInFile(filePath, article) #save all metadata

		# contentProcessing.data2Hugo(article, fileFolder) #turns an article to hugo syntax
	# if file already exists, maybe we don't want to import, but post process only
	else:
		with open(filePath) as fd:
			article = json.loads(fd.read())
		# contentProcessing.data2Hugo(article, fileFolder) #turns an article to hugo syntax
		pass
print "Done"
