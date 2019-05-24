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
#Strategy
#Need to generate the "all" search page and wait for the xml link to generate, then go get it

# +
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from requests import get
import os
from time import sleep
from time import time
from pathlib import Path
import platform

url = 'http://www.clinicaltrials.in.th/index.php?tp=regtrials&menu=trialsearch&smenu=showpb&task=search&task2=showpb'
download_path = '/Users/nicholasdevito/Desktop/TCTR Test'
platform = platform.platform()
cwd = os.getcwd()
download_path = os.path.join(cwd,'ANZCTR Downloads')
parent = str(Path(cwd).parents[0])
# -

if "Darwin" in platform:
    chrome_driver = os.path.join(parent, 'Drivers', 'chromedriver')
elif "Windows" in platform:
    chrome_driver = os.path.join(parent, 'Drivers', 'chromedriver.exe')
else:
    print("No OS/Chromdriver match. OS: {}".format(platform))

# +
chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory" : download_path}
chromeOptions.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(executable_path=chrome_driver, options=chromeOptions)
driver.get(url)
total_trials = (driver.find_element_by_xpath("//span[@class='detail2txt']")).text

xml_button = WebDriverWait(driver, 300).until(ec.presence_of_element_located((By.XPATH, '//a[text()="Export to XML (.zip)"]')))
xml_button.click()
sleep(2)

dl_check = 0
start_time = time()
while dl_check == 0 and time() - start_time < 30:
    count = 0
    for file in os.listdir(download_path):
        if file.endswith(".zip"):
            count = 1
        else:
            count = 0
    if count == 1:
        dl_check = 1
        driver.quit()
    else:
        dl_check = 0
        sleep(2)
# -

total_trials = int(total_trials.split()[1])
print(total_trials)

# +
for file in os.listdir(download_path):
    if file.endswith('.zip'):
        zip_file = file

print(zip_file)
# -

import zipfile
zip_ref = zipfile.ZipFile(download_path + '/' + zip_file, 'r')
zip_ref.extractall(download_path)
zip_ref.close()

# +
for file in os.listdir(download_path):
    if file.endswith('.xml'):
        xml_file = file

print(xml_file)

# +
import xmltodict
import json

xml = open(download_path + '/' + xml_file,  encoding = "ISO-8859-1").read()
trials = xmltodict.parse(xml, encoding = "ISO-8859-1")
# -

tctr_trials = []
for trial in trials['trials']['trial']:
    tctr_trials.append(json.dumps(trial))

len(tctr_trials)

if len(tctr_trials) == total_trials:
    print("Success!: {} trials".format(total_trials))
else:
    print("Error! TCTR Trials {}, Scraped Trials {}".format(total_trials, len(tctr_trials)))

# +
from datetime import date
import csv

def tctr_csv():
    with open('tctr - ' + str(date.todat()) + '.csv','w', newline = '') as tctr_csv:
        writer=csv.writer(tctr_csv)
        for val in tctr_trials:
            writer.writerow([val])

            
#If you want a CSV run this function after the script runs
