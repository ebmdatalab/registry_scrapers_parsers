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
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from time import sleep
import os
from pathlib import Path
import platform

platform = platform.platform()
cwd = os.getcwd()
download_path = os.path.join(cwd,'ANZCTR Downloads')
#adjust this to fit your specific file structure 
parent = str(Path(cwd).parents[0]) 
# -

if "Darwin" in platform:
    chrome_driver = os.path.join(parent, 'Drivers', 'chromedriver')
elif "Windows" in platform:
    chrome_driver = os.path.join(parent, 'Drivers', 'chromedriver.exe')
else:
    print("No OS/Chromedriver match. OS: {}".format(platform))

print(chrome_driver)

# +
#low count ANZCTR test URL
test_anzctr = 'http://www.anzctr.org.au/TrialSearch.aspx?searchTxt=&conditionCategory=Ear&conditionCode=&interventionCodeOperator=OR&interventionCode=&ageGroup=&healthyVolunteers=&gender=All&allocationToIntervention=Randomised&dateOfRegistrationFrom=&dateOfRegistrationTo=&trialStartDateFrom=&trialStartDateTo=&recruitmentCountryOperator=OR&countryOfRecruitment=&primarySponsorType=&fundingSource=&healthCondition=&interventionDescription=&phase=&recruitmentStatus=&registry=ANZCTR&ethicsReview=&studyType=&isBasic=False&postcode=&distance='

#actual URL to use for full download
all_anzctr = 'http://www.anzctr.org.au/TrialSearch.aspx?searchTxt=&conditionCategory=&conditionCode=&interventionCodeOperator=OR&interventionCode=&ageGroup=&healthyVolunteers=&gender=&allocationToIntervention=&dateOfRegistrationFrom=&dateOfRegistrationTo=&trialStartDateFrom=&trialStartDateTo=&recruitmentCountryOperator=OR&countryOfRecruitment=&primarySponsorType=&fundingSource=&healthCondition=&interventionDescription=&phase=&recruitmentStatus=&registry=ANZCTR&ethicsReview=&studyType=&isBasic=False&postcode=&distance='

# +
#this gets the zip file from the ANZCTR

chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory" : download_path}
chromeOptions.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(executable_path=chrome_driver, options=chromeOptions)
driver.get(all_anzctr)
wait = WebDriverWait(driver, 10)
xml_button = wait.until(ec.presence_of_element_located((By.XPATH, '//input[@id="ctl00_body_btnDownload"]')))
driver.execute_script("document.getElementById('ctl00_body_btnDownload').click()",xml_button)
sleep(2)

#makes sure the file is finished downloading before quitting the driver
dl_check = 0
while dl_check == 0:
    count = 0
    for file in os.listdir(download_path):
        if file.endswith(".crdownload"):
            count = count+1
    if count == 0:
        dl_check = 1
        driver.quit()
    else:
        dl_check = 0
        sleep(3)

# +
#gets the name of the downloaded zip file

for file in os.listdir(download_path):
    if file.endswith('.zip'):
        anzctr_zip = file

print(anzctr_zip)


# +
#unzips it and then gets rid of it

import zipfile
zip_ref = zipfile.ZipFile(os.path.join(download_path, anzctr_zip), 'r')
zip_ref.extractall(download_path)
zip_ref.close()

#cleans up xml file after extraction commenting out for now as might find safer way to do this
#for file in os.listdir(download_path):
#    if file.endswith('.zip'):
#        os.remove(os.path.join(download_path, file)
#can also clean up .xsl file if wanted but probably not necessary
# -

import xmltodict
import json
anzctr_trials_list = []

for file in os.listdir(download_path):
    if file.endswith('.xml'):
        with open(os.path.join(download_path, file), encoding="utf8") as xml:
            doc = xmltodict.parse(xml.read())
            anzctr_trials_list.append(str(json.dumps(doc)))

print(anzctr_trials_list[100])

# +
#this creates a csv with no headers and a single column with all trials in json in their own row 
#although moving forward it might be easier to just work in JSON

from datetime import date
import csv

def anzctr_trials():
    with open('anzctr - ' + str(date.today()) + '.csv','w', newline = '')as anzctr_csv:
        writer=csv.writer(anzctr_csv)
        for val in anzctr_trials_list:
            writer.writerow([val])
            
#run this function after the script runs to get a CSV


# -

anzctr_trials()


