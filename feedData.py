import feedparser
import datetime

def feed2data(url):
	""" From a feed returns required data """

	d = feedparser.parse(url)
	last =  d['feed']['updated_parsed']
	last_update = datetime.datetime(*last[:6])

	result = {"last_update":last_update}

	items = []
	for entry in d["entries"]:
		# Published Time
		published = entry["published_parsed"]
		published_time = datetime.datetime(*published[:6])

		# Link
		#link = entry['links'][0]['href']
		link = entry['id']

		# Title
		title = entry["title"]

		# Author
		author = {}
		if "twitter" in entry:
			twitter = entry['twitter']
			author["twitter"] = twitter

		for img in entry["media_content"]:
			if "gravatar" in img["url"]:
				author["image"] = img["url"]

		# We keep only the first author
		author["name"] = entry["authors"][0]["name"]

		# Images
		images = []
		for img in entry["media_content"]:
			if "gravatar" not in img["url"]:
				images.append(img["url"])

		# Tags
		tags = []
		for tag in entry["tags"]:
			tags.append(tag.term)

		# Slug 
		slug = published_time.strftime("%Y-%m-%d")+"_"+"-".join(title.split())

		entryDict = {"slug": slug, "published_time": published_time, "link": link, "title": title, "author": author, "tags":tags, "images":images}
		items.append(entryDict)

	result["items"] = items

	return result