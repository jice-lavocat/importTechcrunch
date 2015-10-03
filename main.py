from feedData import feed2data
import json
import os, errno
import datetime
from goose import Goose

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
mkdir_p(metaDataPath)
mkdir_p(articlePath)

# We keep only one file per hour
fileName = data["last_update"].strftime("%Y-%m-%d_%H") + ".json"
filePath = os.path.join(metaDataPath, fileName)

dumpInFile(filePath, data)

for article in data["items"]:
	fileName = article["slug"] + ".json"
	filePath = os.path.join(articlePath, fileName)
	# Add file if not existing yet
	if not os.path.isfile(filePath):
		# import the article via Goose
		g = Goose()
		art = g.extract(article["link"])


		goose = {"title" : art.title, "content": art.content_html}


		article["goose"] = goose

		dumpInFile(filePath, article)
	else:
		pass
print "Done"
