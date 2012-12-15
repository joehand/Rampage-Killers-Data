Motivated by [Enrico Bertini](https://twitter.com/FILWD/status/279827195495591936), here is a collection of data scraped from the Wikipedia pages for [Rampage Killers](http://en.wikipedia.org/wiki/List_of_rampage_killers).

***Let me know what you make with it.*** I may take a shot as a visualization as well.

##Data Files
**All the data is in data folder. `table-data.md` is just an html version so you can look through it.**

There are two full data sets (one CSV, one JSON). The other files are each individual tables as shown in wikipedia. The table name has been added to all sets for reference. 

Data has some cleanliness issues. It is somewhat easy to address any systemic issues when scraping data. Some cleaning will need to be done by hand. 

The reference links are useless right now. If I have some time, I can figure out how to get the reference links off wikipedia in the file as well.

##Python scripts
The scripts use beautiful soup to parse the wikipedia pages. Wikipedia requires send a user-agent, urllib2 is used for that.

###Helpful items in Python scripts
There are a few pieces that may be helpful to other people in scraping wikipedia again. 

####Connecting to Wikipeida & Getting a page:

```python
import urllib2
from bs4 import BeautifulSoup 

#Set Our Page Title and make it URL friendly
article = "Wiki_page_title" #make sure this is the one after wiki/ in the url
article = urllib2.quote(article)

#Builds the handler to open API
opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')] #wikipedia requires user-agent

#Get the Page Content and Read it
resource = opener.open("http://en.wikipedia.org/wiki/" + article)
data = resource.read()
resource.close()
```

####Getting all links matching a regex

```python
import re

#Find all the links we need
page = BeautifulSoup(data)

myLinks = [] #will use this to save links
match = re.compile('(List\_of\_rampage\_killers:\_)') # find only the links we want

# check links
for link in page.findAll('a'):
    href = link.get('href')
    if href:
        try:
            href = link.get('href')
            if re.search(match, href):
                href = re.sub('\/wiki\/', '', href) #get just the link title
                if not any(href in s for s in fullTableLinks): #links are probably multiple times on page
                    myLinks.append(href)
        except KeyError:
            pass

```

#### Grab all wikitable (a html class) on a page

First connect to the page (shown above)

```python

# Fetch HTML Table Rows
soup = BeautifulSoup(data) #data is our html page (see above)
fullTable = soup.find_all('table', 'wikitable') #may have more than one... fun!

pageTables = []

if fullTable:
    for i, table in enumerate(fullTable):
        if i != 0:
            header = header + str(i) #set this however you want to index multiple tables
        table = {'header': header, 'content': table }
        pageTables.append(table)

```
#### Parsing Table Data from Wikipedia

```python
for table in pageTables:
    #thanks to this gist for help through the rest here: https://gist.github.com/1501715

    tableContent = table['content']
    #grab all the rows
    rows = tableContent.findAll('tr')

    for row in rows[0:1]:
        keys = {}
        for i, field in enumerate(row.findAll('th')):
            text = re.split('\(', field.text)[0] #cut out anything after ()
            text = re.sub('\s+','_', text).lower() #replace spaces with _ and make lowercase

    #create tableRows
    tableRows = []
    for row in rows[1:]:
        rowmap = {}
        for i, field in enumerate(row.findAll('td')):
            """
            CLEAN YOUR DATA HERE (see script for example)
            """
            fieldText = field.text.strip() #remove outside whitespaces

            rowmap[keys[i]] = fieldText #add to our dict
        if rowmap:
            tableRows.append(rowmap)

    if len(tableRows):
        #Create Flat JSON file
        print ("Exporting JSON Data to " + header + '.json')
        f = open('data/header + '.json', 'w')
        f.write(json.dumps(tableRows, sort_keys=True, indent=4))
        f.close()
```

