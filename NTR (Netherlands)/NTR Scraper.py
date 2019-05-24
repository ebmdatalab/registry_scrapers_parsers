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

from requests import get
from bs4 import BeautifulSoup
import re
import nest_asyncio
nest_asyncio.apply()
from fake_useragent import UserAgent
from requests_html import HTMLSession
ua = UserAgent()
headers = {'User-Agent': ua.random}
ntr_search = 'https://www.trialregister.nl/trials'
url = 'https://www.trialregister.nl/trial/'

#This gets the home page which gets us the number of trials. Trial IDs are in sequential order and in the URLs
session = HTMLSession()
r = session.get(ntr_search, headers=headers)
r.html.render(wait=1,sleep=1)
home = r.html.text
search = re.compile('\d{4,5} trials found')
raw_count_string = search.findall(home)[0]
count = re.compile('\d{4,5}')
trial_count = int(count.findall(raw_count_string)[0])
print(trial_count)

#get a list of trial IDs for later from this
trial_ids =  list(range(1,trial_count+1))

#for testing
trial_ids = list(range(1,11))

# +
labels = ['Acronym', 'Title', 'Scientific title', 'Summary', 'Status', 'Study type', 'Control group', 
          'Grouping', 'Arms', 'Masking', 'Target size', 'Inclusion criteria', 'Exclusion criteria', 
         'Start date', 'Stop date', 'Diseases', 'Hypothesis', 'Interventions', 'Primary outcome', 
         'Secondary outcome', 'Sponsors', 'Time points', 'MEC approved', 'Multicenter', 'Randomised', 
         'Plan to share IPD', 'IPD plan description', 'Publications', 'Issueing body', 'Source ID', 
         'Funding sources', 'Old NTR ID', 'Date registered', 'URL', 'Contact', 'Registrant']

ntc_trials = []

for id in trial_ids:
    session = HTMLSession()
    t = session.get(url + str(id), headers=headers)
    t.html.render(wait=1,sleep=1)
    trial = t.html.find('.jss1')[0].text
    newlines = trial.splitlines(True)
    newlines_slice = newlines[8:]
    newlines_slice.remove('Show audit trail\n')
    trial_info = []
    for i in newlines_slice:
        x = i.rstrip()
        trial_info.append(x)
    trial_info = list(filter(None, trial_info))
    i_list = []
    for label in labels:
        i_list.append(trial_info.index(label))
    trial_dict = {}
    trial_dict['Trial ID'] = trial_info[0][6:]
    for idx, i in enumerate(i_list):
        try:
            trial_dict[labels[idx]] = trial_info[i+1:i_list[idx+1]]
            if len(trial_dict[labels[idx]]) == 1:
                trial_dict[labels[idx]] = trial_dict[labels[idx]][0]
        except IndexError:
            trial_dict[labels[idx]] = trial_info[i+1:]
            if len(trial_dict[labels[idx]]) == 1:
                trial_dict[labels[idx]] = trial_dict[labels[idx]][0]
    ntc_trials.append(trial_dict)
# -

if len(ntc_trials) == trial_count:
    print('Scrape Successful - {} records scraped'.format(trial_count))
else:
    print('Issue with Scrape - {} difference between trial_count and scraped trials'.format(trial_count - len(ntc_trials)))

# +
labels = ['Trial ID', 'Acronym', 'Title', 'Scientific title', 'Summary', 'Status', 'Study type', 'Control group', 
          'Grouping', 'Arms', 'Masking', 'Target size', 'Inclusion criteria', 'Exclusion criteria', 
         'Start date', 'Stop date', 'Diseases', 'Hypothesis', 'Interventions', 'Primary outcome', 
         'Secondary outcome', 'Sponsors', 'Time points', 'MEC approved', 'Multicenter', 'Randomised', 
         'Plan to share IPD', 'IPD plan description', 'Publications', 'Issueing body', 'Source ID', 
         'Funding sources', 'Old NTR ID', 'Date registered', 'URL', 'Contact', 'Registrant']

from datetime import date
import csv

def ntc_csv():
    with open('ntc - ' + str(date.today()) + '.csv','w', newline = '') as ntc_csv:
        writer=csv.DictWriter(ntc_csv,fieldnames=labels)
        writer.writeheader()
        writer.writerows(ntc_trials)
# -




