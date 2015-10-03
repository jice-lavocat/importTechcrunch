from feedData import feed2data
import json
import os, errno
import datetime


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
	    #print unicode(path) + " : created"

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
mkdir_p(metaDataPath)

fileName = data["last_update"].strftime("%Y-%m-%d_%H-%M") + ".json"
filePath = os.path.join(metaDataPath, fileName)

dumpInFile(filePath, data)
print "Done"
