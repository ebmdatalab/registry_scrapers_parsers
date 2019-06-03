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
from requests import ConnectionError
from bs4 import BeautifulSoup
import re
from time import sleep
from time import time
from random import randint
from IPython.core.display import clear_output
from warnings import warn
import pandas as pd
import random

# +
#pull single page to test and get max page number
url = 'https://www.clinicaltrialsregister.eu/ctr-search/search?query=&resultsstatus=trials-with-results&page1'
response = get(url, verify = False)
html = response.content

#what does our parsed html look like?
soup = BeautifulSoup(html, "html.parser")
# -

#gets max page number
number_of_pages = soup.find('div', {'class': 'margin-bottom: 6px;'})
max_page_link = str(number_of_pages.find_all('a')[-1])
max_page = re.findall(r'\d+', max_page_link)[0]
print(max_page)

#setting up variables for page URLs
euctr_base_url = 'https://www.clinicaltrialsregister.eu'
euctr_results_search_page = '/ctr-search/search?query=&resultsstatus=trials-with-results&page='

#variables needed for first scrape
pages = [str(i) for i in range(1,int(max_page)+1)]
trial_ids = []
results_urls = []
start_time = time()
requests = 0
print(pages[-1])

# +
#this crawls every trial that comes up with a search result of trials with results on the EUCTR

for page in pages:
    
    #make this request
    tries=3
    for i in range(tries):
        try:
            response = get(euctr_base_url + euctr_results_search_page + page, verify = False)
            break
        except ConnectionError as e:
            if i < tries - 1:
                sleep(2)
                continue
            else:
                raise
    
    #pause to look like a human
    #sleep(random.uniform(0,0.2)) #not needed at the moment for this
    
    #mointor the requests to ensure everything is working
    requests += 1
    elapsed_time = time() - start_time
    print('Request: {}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))
    clear_output(wait = True)
    
    # Throw a warning for a non-200 status code
    if response.status_code != 200:
        warn('Request: {}; Status code: {}'.format(requests, response.status_code))

    #Break the looop if we exceed the number of requests which will need to change when i do full scrape
    if requests > int(max_page):
        warn('Number of requests was greater than expected.')  
        break 
    
    #Parse the requests
    page_html = BeautifulSoup(response.text, 'html.parser')
    
    #select all the trial tables
    trial_tables = page_html.find_all('table', {'class': 'result'})
    
    #get the trial id and the trial url for each thing
    for trial_table in trial_tables:
        trial_id = trial_table.input.get('value')
        trial_ids.append(trial_id)
        url = euctr_base_url + trial_table.find_all('a')[-1].get('href')
        results_urls.append(url)

# +
results_trial_id = []
global_end_of_trial_date = []
first_publication_date = []
current_publication_date = []
results_version = []
results_type = []
start_time_2 = time()
requests_2 = 0
trial_number = 0

def tds_strip(td_table, td):
    return td_table[td].div.get_text().strip()


# +
#this takes the urls from the above scrape, and crawls them for results information

for result_url in results_urls: 
    
    #make this request
    tries=3
    for i in range(tries):
        try:
            requests_2 += 1
            response = get(result_url, verify = False)
            break
        except ConnectionError as e:
            if i < tries - 1:
                sleep(2)
                continue
            else:
                raise     
    
    #pause to look like a human
    #sleep(random.uniform(0,0.5)) #uncomment if needed
    
    #mointor the requests to ensure everything is working
    trial_number += 1
    elapsed_time = time() - start_time_2
    print('Trial Number: {}; Request: {}; Frequency: {} requests/s'.format(trial_number, requests_2, requests_2/elapsed_time))
    clear_output(wait = True)
    
    # Throw a warning for a non-200 status code
    if response.status_code != 200:
        warn('Request: {}; Status code: {}'.format(requests_2, response.status_code))

    #Break the looop if we exceed the number of requests which will need to change when i do full scrape
    if requests_2 > len(results_urls):
        warn('Number of requests was greater than expected.')  
        break 
    
    #Parse the requests
    page_html = BeautifulSoup(response.text, 'html.parser')
    
    #select all the results tables
    leg_text = page_html.find('div', id = 'synopsisLegislationNote')
    trial_tables = page_html.find_all('table')[4]
    td_value = trial_tables.find_all('td', class_ = 'valueColumn')
    td_label = trial_tables.find_all('td', class_ = 'labelColumn') 
    trial_id = trial_tables.find_all('a')[0].get_text()
    results_trial_id.append(trial_id)
    global_end_date = tds_strip(td_value,3)
    global_end_of_trial_date.append(global_end_date)
    
    if td_label[-1].div.get_text().strip() == 'Summary report(s)' and leg_text:
        first_pub = tds_strip(td_value,11)
        first_publication_date.append(first_pub)
        current_pub = tds_strip(td_value,10)
        current_publication_date.append(current_pub)
        version = td_value[9].get_text().strip()
        results_version.append(version)
        results_type.append("Document")
    
    elif td_label[-1].div.get_text().strip() == 'Summary report(s)' and not leg_text:
        first_pub = tds_strip(td_value,7)
        first_publication_date.append(first_pub)
        current_pub = tds_strip(td_value,6)
        current_publication_date.append(current_pub)
        version = td_value[5].get_text().strip()
        results_version.append(version)
        results_type.append("Mixed")
        
    else:
        first_pub = tds_strip(td_value,7)
        first_publication_date.append(first_pub)
        current_pub = tds_strip(td_value,6)
        current_publication_date.append(current_pub)
        version = td_value[5].get_text().strip()
        results_version.append(version)
        results_type.append("Tabular")
# -

if len(trial_ids) == len(results_trial_id):
    print("All Scraped")
else:
    print("Error in Scrape: Difference of {} trials between first and second scrape".format(len(trial_ids) - len(results_trial_id)))

# +
results_df = pd.DataFrame({'trial_id': results_trial_id,
                       'global_trial_end_date': global_end_of_trial_date,
                       'first_pub_date': first_publication_date,
                       'current_pub_date': current_publication_date,
                       'version': results_version,
                       'results_type': results_type
                          })

results_df.tail()

# +
#some data cleaning

cleaned = 0
for index, row in results_df.iterrows():
    if row.first_pub_date == 'No':
        results_df.at[index, 'first_pub_date'] = None
        results_df.at[index, 'current_pub_date'] = None
        results_df.at[index, 'version'] = None
        results_df.at[index, 'results_type'] = 'None Available'
        cleaned += 1

#dates to datetime
results_df['global_trial_end_date'] = pd.to_datetime(results_df['global_trial_end_date'])
results_df['first_pub_date'] = pd.to_datetime(results_df['first_pub_date'])
results_df['current_pub_date'] = pd.to_datetime(results_df['current_pub_date'])
print("Cleaned {} Rows".format(cleaned))
# -

results_df.dtypes

#make a csv
results_df.to_csv('euctr_results_scrape_june2019.csv')


