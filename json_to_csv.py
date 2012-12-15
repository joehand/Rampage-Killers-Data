#!/usr/bin/env python
# encoding: utf-8
"""
json_to_csv.py


@Author: Joe Hand
@Description: Convert JSON to CSV
"""


"""
JSON FORMAT:

{
    "additional_notes": "Sentenced to 21 years in prison\nTwo more died trying to escape", 
    "country": "Norway", 
    "date": "07/22", 
    "full_date": "07/22/2011", 
    "injured": "242", 
    "killed": "75", 
    "location": "Oslo & Ut\u00f8ya", 
    "perpetrator": "Breivik, Anders Behring, 32", 
    "ref.": "", 
    "table_name": "religious_political_or_racial_crimes", 
    "w": "F\u00a0E"
}, 

"""

#Import the necessary libraries
#	json: easy json exporting

import json
import csv
import sys

fileToConvert = 'data/full_incidence_data.json'
fileToWrite = 'data/full_incidence_data.csv'

#open our clean JSON file
f = open(fileToConvert)
data = json.load(f)
f.close()
print('got data')

#make new CSV file to save data to
f = open(fileToWrite, 'w')
csv_file = csv.writer(f)

print('writing...')

tableHeader = []
for key in data[0].keys():
   tableHeader.append(key.encode('utf-8'))

# Write CSV Header
csv_file.writerow(tableHeader)

for item in data:
    #make new CSV row for each JSON object
    row = []
    for key, value in item.iteritems():
        #need to be careful encoding
        row.append(value.encode('utf-8'))
    #write our row
    csv_file.writerow(row)

f.close()