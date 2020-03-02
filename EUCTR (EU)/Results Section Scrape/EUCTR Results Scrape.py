# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from requests import get
from requests import ConnectionError
from bs4 import BeautifulSoup
import re
from time import time
from time import sleep
from warnings import warn
import pandas as pd

from tqdm import tqdm

#try:
#    get_ipython
#    from tqdm.notebook import tqdm
#except NameError:
#    from tqdm import tqdm
    
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
def get_url(url):
    response = get(url, verify = False)
    html = response.content
    soup = BeautifulSoup(html, "html.parser")
    return soup


# +
url = 'https://www.clinicaltrialsregister.eu/ctr-search/search?query=&resultsstatus=trials-with-results&page1'
soup = get_url(url)

#gets max page number
number_of_pages = soup.find('div', {'class': 'margin-bottom: 6px;'})
max_page_link = str(number_of_pages.find_all('a')[-1])
max_page = re.findall(r'\d+', max_page_link)[0]
print(max_page)

# +
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

for page in tqdm(pages):
    
    #make this request
    tries=3
    for i in range(tries):
        try:
            page_html = get_url(euctr_base_url + euctr_results_search_page + page)
            break
        except ConnectionError as e:
            if i < tries - 1:
                sleep(2)
                continue
            else:
                raise
    
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

def scrape_info(fp_n, cp_n, v_n):
    first_pub = tds_strip(td_value, fp_n)
    current_pub = tds_strip(td_value, cp_n)
    version = td_value[v_n].get_text().strip()
    return first_pub, current_pub, version


# +
#this takes the urls from the above scrape, and crawls them for results information

for result_url in tqdm(results_urls): 
    
    #make this request
    tries=6
    for i in range(tries):
        try:
            page_html = get_url(result_url)
            break
        except ConnectionError as e:
            if i < tries - 1:
                sleep(2)
                continue
            else:
                raise     
    
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
        fp, cp, v = scrape_info(11, 10, 9)
        first_publication_date.append(fp)
        current_publication_date.append(cp)
        results_version.append(v)
        results_type.append("Document")
    
    elif td_label[-1].div.get_text().strip() == 'Summary report(s)' and not leg_text:
        fp, cp, v = scrape_info(7, 6, 5)
        first_publication_date.append(fp)
        current_publication_date.append(cp)
        results_version.append(v)
        results_type.append("Mixed")
        
    else:
        fp, cp, v = scrape_info(7, 6, 5)
        first_publication_date.append(fp)
        current_publication_date.append(cp)
        results_version.append(v)
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
results_df.to_csv('euctr_results_scrape_feb2020.csv')


