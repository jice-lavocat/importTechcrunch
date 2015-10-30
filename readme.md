Fetch the rss feed from techcrunch at a given hour.

1/ Extract meta data, and saves them in 'data' > 'metadata' > 2015-10-21_15.json (if day is 21 Oct 2015 - 16h). The file has a list of items with all the available info from the rss feed : title, list images, url, list des tags

2/ Create a folder in 'data' > 'articles' > '2015_10_21_title'. Then the script start goose on the url and create files :
	* one folder teaser with one teaser
	* one folder thumbnail with one thumbnail
	* a json file with metadata taken from Goose and from the RSS feed

3/ Translation paragraph by paragraph is made and inserted into the json file

4/ The interesting info are exported to the HUGO format in .md file