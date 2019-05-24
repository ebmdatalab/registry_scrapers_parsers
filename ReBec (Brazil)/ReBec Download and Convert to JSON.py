# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
#https://stackoverflow.com/questions/51114736/xml-file-download-blocked-in-selenium-chromedriver
from requests import get
from bs4 import BeautifulSoup
import re
import os
from pathlib import Path
import platform
from xml.sax.saxutils import escape
import string

platform = platform.platform()
cwd = os.getcwd()
download_path = os.path.join(cwd,'Rebec Downloads')
#adjust this to fit your specific file structure 
parent = str(Path(cwd).parents[0]) 

# +
base_rebec_url = 'http://www.ensaiosclinicos.gov.br/rg/?page='

if "Darwin" in platform:
    chrome_driver = os.path.join(parent, 'Drivers', 'chromedriver')
elif "Windows" in platform:
    chrome_driver = os.path.join(parent, 'Drivers', 'chromedriver.exe')
else:
    print("No OS/Chromedriver match. OS: {}".format(platform))

# +
#Quick way to get max_page count
url = base_rebec_url + '1'
response = get(url, verify = False)
html = response.content

#gets parsed HTML
soup = BeautifulSoup(html, "html.parser")

number_of_pages = soup.find('div', {'class': 'pagination'})
max_page = number_of_pages.find_all('a')[-3].get_text()
print(max_page)
# -

#getting the full trial count
home_page = get('http://www.ensaiosclinicos.gov.br')
hp_html = home_page.content
hp_soup = BeautifulSoup(hp_html, "html.parser")
tags = hp_soup.find_all('p')
for p in tags:
    if "ensaios publicados." in str(p):
        trial_count = int(p.find('span').text)
print(trial_count)

# +
#everything we need to run our selenium crawler
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep

page_list = [str(i) for i in range(2,int(max_page)+1)]
#after testing put this for full download: 'int(max_page)+1' instead of '5'

# +
#this goes to the first search page, downloads the xml, then does that for every other page

chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory" : download_path,
        'profile.managed_default_content_settings.images':2,
        'disk-cache-size': 4096,
        'safebrowsing.enabled': 'false'}
chromeOptions.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(executable_path=chrome_driver, options=chromeOptions)
driver.get(base_rebec_url + '1')
#sleep(3)
driver.find_element_by_id("chk_toggle_selection").click()
driver.find_element_by_xpath("//input[@value='Download selected as OpenTrials XML format']").click()
#sleep(3)
for page in page_list:
    driver.find_element_by_link_text(page).click()
    driver.find_element_by_id("chk_toggle_selection").click()
    driver.find_element_by_xpath("//input[@value='Download selected as OpenTrials XML format']").click()
    #sleep(1)
sleep(5)
driver.quit()

 

# +
#quick check to make sure we got the correct number of files
dl_counter = 0
for file in os.listdir(download_path):  
    if file.endswith('.xml'):
        dl_counter += 1

if dl_counter == max_page:  #4 is here just for testing, use 'max_page' variable for full implementation
    print("Full Download Successful")
else:
    print("Missing " + str(int(max_page)  - dl_counter) + " File(s)") #once again, replace the 4 here with 'max_page' in full implementation

# +
#think if this can help? https://stackoverflow.com/questions/4324790/removing-control-characters-from-a-string-in-python
#or this https://stackoverflow.com/questions/17480656/remove-ascii-control-characters-from-text-file-python/43521569

import xmltodict
import json

#gets each trial and adds it to a list a json

rebec_trials = []
nonprintable = set([chr(i) for i in range(128)]).difference(string.printable)

for file in os.listdir(download_path):
    if file.endswith('.xml'):
        with open(os.path.join(download_path, file), encoding = 'utf-8') as xml:
            filtered_xml = "".join([b for b in xml.read() if b not in nonprintable])
            trials = xmltodict.parse(filtered_xml)
            for trial in trials['trials']['trial']:
                rebec_trials.append(json.dumps(trial))
# -

#quick check to make sure things worked
print(rebec_trials[114])

#check
if len(rebec_trials) == trial_count:
    print("Success!: {} trials".format(trial_count))
else:
    print("Scrape Issue: {} on Rebec, {} in scrape".format(trial_count, len(rebec_trials)))

# +
#creates a csv with no headers and a single column with all trials in json in their own row.

from datetime import date
import csv

def rebec_csv():
    with open('rebec - ' + str(date.today()) + '.csv','w', newline = '')as rebec_csv:
        writer=csv.writer(rebec_csv)
        for val in rebec_trials:
            writer.writerow([val])

# +
#rebec_csv()
# -


