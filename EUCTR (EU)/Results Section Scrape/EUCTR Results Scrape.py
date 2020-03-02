import os
os.getcwd()
os.chdir('/Users/nicholasdevito/Desktop/euctr_res_scrape')
os.getcwd()

from requests import get, ConnectionError
from bs4 import BeautifulSoup
import re
from time import time, sleep
import pandas as pd
from multiprocessing import Pool
from tqdm import tqdm

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

start_time = time()

def get_url(url):
    response = get(url, verify = False)
    html = response.content
    soup = BeautifulSoup(html, "html.parser")
    return soup

url = 'https://www.clinicaltrialsregister.eu/ctr-search/search?query=&resultsstatus=trials-with-results&page1'
soup = get_url(url)

#gets max page number
number_of_pages = soup.find('div', {'class': 'margin-bottom: 6px;'})
max_page_link = str(number_of_pages.find_all('a')[-1])
max_page = re.findall(r'\d+', max_page_link)[0]
print(f"max_page: {max_page}")

#pages = [str(i) for i in range(1,int(max_page)+1)]
pages = [str(i) for i in range(1,5+1)]

#setting up variables for page URLs
euctr_base_url = 'https://www.clinicaltrialsregister.eu'
euctr_results_search_page = '/ctr-search/search?query=&resultsstatus=trials-with-results&page='

def try_to_connect(tries, url):
    for i in range(tries):
        try:
            page_html = get_url(url)
            break
        except ConnectionError:
            if i < tries - 1:
                print('Retrying {}...'.format(url))
                sleep(2)
                continue 
            else:
                print('This URL failed: {url}')
                page_html = None
    return page_html

def get_trials(page):
	euctr_base_url = 'https://www.clinicaltrialsregister.eu'
	euctr_results_search_page = '/ctr-search/search?query=&resultsstatus=trials-with-results&page='
	
	#make the request
	page_html = try_to_connect(5, euctr_base_url + euctr_results_search_page + page)
	
	#get the tables
	trial_tables = page_html.find_all('table', {'class': 'result'})
	trial_info = []
	for trial_table in trial_tables:
		trial_id = trial_table.input.get('value')
		url = euctr_base_url + trial_table.find_all('a')[-1].get('href')
		trial_tuple = (trial_id, url)
		trial_info.append(trial_tuple)
	return trial_info


if __name__ == '__main__':
    with Pool() as p:
        trial_info = list(tqdm(p.imap(get_trials, pages), total=len(pages)))

tuples = list(trial_info)
tuples = [t for sublist in tuples for t in sublist]

print(f'There are {len(tuples)} trials')

def tds_strip(td_table, td):
    return td_table[td].div.get_text().strip()

def scrape_info(td_value, fp_n, cp_n, v_n):
    first_pub = tds_strip(td_value, fp_n)
    current_pub = tds_strip(td_value, cp_n)
    version = td_value[v_n].get_text().strip()
    return first_pub, current_pub, version


def get_results_info(tup):
    #make the request
    page_html = try_to_connect(5, tup[1])
    
    #select all the results tables
    leg_text = page_html.find('div', id = 'synopsisLegislationNote')
    trial_tables = page_html.find_all('table')[4]
    td_value = trial_tables.find_all('td', class_ = 'valueColumn')
    td_label = trial_tables.find_all('td', class_ = 'labelColumn') 
    
    r_dict = {}
    r_dict['trial_id'] = tup[0]
    r_dict['global_trial_end_date'] = tds_strip(td_value,3)

    if td_label[-1].div.get_text().strip() == 'Summary report(s)' and leg_text:
        fp, cp, v = scrape_info(td_value, 11, 10, 9)
        r_dict['first_pub_date'] = fp
        r_dict['current_pub_date'] = cp
        r_dict['version'] = v
        r_dict['results_type'] = 'Document'
    
    elif td_label[-1].div.get_text().strip() == 'Summary report(s)' and not leg_text:
        fp, cp, v = scrape_info(td_value, 7, 6, 5)
        r_dict['first_pub_date'] = fp
        r_dict['current_pub_date'] = cp
        r_dict['version'] = v
        r_dict['results_type'] = 'Mixed'
        
    else:
        fp, cp, v = scrape_info(td_value, 7, 6, 5)
        r_dict['first_pub_date'] = fp
        r_dict['current_pub_date'] = cp
        r_dict['version'] = v
        r_dict['results_type'] = 'Tabular'

    return r_dict

if __name__ == '__main__':
    with Pool() as p:
        results = list(tqdm(p.imap(get_results_info, tuples), total=len(tuples)))

results = list(results)

if len(tuples) == len(results):
    print("All Scraped")
else:
    print("Error in Scrape: Difference of {} trials between first and second scrape".format(len(tuples) - len(results)))

results_df = pd.DataFrame(results)

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

results_df.to_csv('euctr_results_scrape_test.csv')