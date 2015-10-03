import re


def html2flat(html):
	""" Takes html and return clean html where :
			* <a> have been removed
	"""

	cleanHtml = html
	cleanHtml = re.sub('</?[div|a|iframe^>]*>', '', cleanHtml)

	return cleanHtml