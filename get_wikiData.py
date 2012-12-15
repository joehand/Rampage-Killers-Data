#!/usr/bin/env python
# encoding: utf-8
"""
get_wikiData.py


@Author: Joe Hand
@Description: This will get the information from the wikipedia entry for "List of rampage killers"
			  We will use the Wikiepedia API (http://en.wikipedia.org/w/api.php)
			  
			  Source Data: http://en.wikipedia.org/wiki/List_of_rampage_killers
			  
			  It will output both a JSON file.

              Each table on main page is restricted to 15 entries, we have to visit links to full tables.
"""

#Import the necessary libraries
#	urllib2: a high-level interface for fetching data across the World Wide Web
#	re: python regular expressions
#	json: easy json exporting
#	BeautifulSoup: Beautiful Soup is a Python library designed for quick turnaround projects like screen-scraping

#note: BeautifulSoup needs to be installed
import urllib2
import re
import json
import sys
from bs4 import BeautifulSoup 


#Set Our Page Title and make it URL friendly
article = "List_of_rampage_killers"
article = urllib2.quote(article)

#Builds the handler to open API
opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')] #wikipedia requires user-agent

#Get the Page Content and Read it
print ("Getting HTML...")
resource = opener.open("http://en.wikipedia.org/wiki/" + article)
data = resource.read()
resource.close()

#Find all the links we need
print("Get links to full tables")
page = BeautifulSoup(data)

fullTableLinks = [] #will use this to save links to full tables not on this page
match = re.compile('(List\_of\_rampage\_killers:\_)') # find only the links we want

# check links for full tables
for link in page.findAll('a'):
    href = link.get('href')
    if href:
        try:
            href = link.get('href')
            if re.search(match, href):
                href = re.sub('\/wiki\/', '', href) #get just the page title
                if not any(href in s for s in fullTableLinks): #links are probably linked multiple times on page
                    fullTableLinks.append(href)
        except KeyError:
            pass

#we now have all links for the full tables, lets get the tables in this page that aren't linked elsewhere before we visit those pages
pageTables = []

for header in page.find_all('h2'):
    sectionHead = header.find('span', {'class' : 'mw-headline'})

    if sectionHead:
        try:
            intoPara = header.next_sibling.next_sibling #two siblings down to skip whitespace
            italics = intoPara.find('i') #full list available elsewhere text
            if italics:
                pass
            else:
                tableContent = intoPara.next_sibling.next_sibling
                if tableContent:
                    tableContent = tableContent
                    header = header.find('span', {'class': 'mw-headline'}).contents[0]
                    table = {'header': header, 'content': tableContent }
                    pageTables.append(table)
        except KeyError:
            pass


print ("Visiting additional pages for full tables...")
# We have all the tables on this page, now we visit the other pages to get those tables
for link in fullTableLinks:
    #Set Our Page Title and make it URL friendly
    article = urllib2.quote(link)

    #Builds the handler to open API
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')] #wikipedia requires user-agent

    #Get the Page Content and Read it
    print ("Getting HTML for new page at " + link)
    resource = opener.open("http://en.wikipedia.org/wiki/" + article)
    data = resource.read()
    resource.close()

    # Fetch HTML Table Rows
    soup = BeautifulSoup(data)
    header = re.sub('(List\_of\_rampage\_killers:\_)', '', link)
    fullTable = soup.find_all('table', 'wikitable') #may have more than one... fun!

    if fullTable:
        for i, table in enumerate(fullTable):
            if i != 0:
                header = header + str(i)
            table = {'header': header, 'content': table }
            pageTables.append(table)


#write all tables to an html just so we can see it
print("write to an md just so we can see it...")
f = open('table-data.md', 'w')
for table in pageTables:
    f.write('<h2>' + table['header'].encode("utf8") + '</h2>' + '\n')
    f.write(table['content'].prettify().encode("utf8"))
    f.write('\n')
f.close()

print ("Organizing Data and printing JSON files...")

fullList = []
for table in pageTables:
    #thanks to this gist for help through the rest here: https://gist.github.com/1501715
    #grab all the rows
    header = table['header']
    header = re.sub('\s+','_', header).lower() #replace spaces with _ and make lowercase
    header = re.sub(',+','', header) #remove commas

    tableContent = table['content']
    rows = tableContent.findAll('tr')

    for row in rows[0:1]:
        keys = {}
        for i, field in enumerate(row.findAll('th')):
            if i != 0:
                text = re.split('\(', field.text)[0] #cut out anything after ()
                text = re.sub('\s+','_', text).lower() #replace spaces with _ and make lowercase
                if i == 3:
                    text = 'full_date' #changing from date/year to just full date
                keys[i] = text
    """
    # Column Keys, used to match the items for each row, created from header
    keys = {
        0: 'meainingless number',
        1: 'perpetrator',
        2: 'date',
        3: 'year',
        4: 'location',
        5: 'country',
        6: 'killed',
        7: 'injured',
        8: 'weapon',
        9: 'notes',
        10: 'ref'
    }
    """

    #create incidences
    incidences = []
    for row in rows[1:]:
        rowmap = {}
        for i, field in enumerate(row.findAll('td')):
            if i != 0:
                """
                TODO: data cleanup can go here for each field
                """
                fieldText = field.text.strip() #remove outside whitespaces

                if i == 2:
                    """
                    Cleaning up dates here. Most (hopefully all) of them come in like this:
                        12.04\nDec. 4
                    We will take the first four chars and make it real date
                    """
                    fieldText = re.sub("\.", "/", fieldText[:5])
                elif i == 3:
                    fieldText = rowmap[keys[i-1]] + '/' + str(fieldText)

                rowmap[keys[i]] = fieldText #add to our dict
        if rowmap:
            rowmap['table_name'] = header
            incidences.append(rowmap)
            fullList.append(rowmap) #append to our full list array for a single file

    if len(incidences):
        #Create Flat JSON file
        print ("Exporting JSON Data to " + 'incidence_data-' + header + '.json')
        f = open('data/incidence_data-' + header + '.json', 'w')
        f.write(json.dumps(incidences, sort_keys=True, indent=4))
        f.close()

print ("Exporting all incidences to single file")
f = open('data/full_incidence_data.json', 'w')
f.write(json.dumps(fullList, sort_keys=True, indent=4))
f.close()

sys.exit()