import re
from translate import translator
import lxml.html
from lxml import etree

def html2flat(html):
	""" Takes html and return clean html where :
			* <a> have been removed
	"""

	cleanHtml = html
	cleanHtml = re.sub('</?[div|a|iframe^>]*>', '', cleanHtml)

	return cleanHtml

def translateHtml(html):
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