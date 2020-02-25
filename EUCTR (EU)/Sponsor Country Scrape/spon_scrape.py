import os
os.getcwd()
os.chdir('/Users/nicholasdevito/Desktop/euctr_spon_scrape')
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

url = 'https://www.clinicaltrialsregister.eu/ctr-search/search?query=&page=1'
soup = get_url(url)

#gets max page number
number_of_pages = soup.find('div', {'class': 'margin-bottom: 6px;'})
max_page_link = str(number_of_pages.find_all('a')[-1])
max_page = re.findall(r'\d+', max_page_link)[0]

pages = [str(i) for i in range(1,int(max_page)+1)]
#below is for testing
#pages = [str(i) for i in range(1,10+1)]


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
    base_search_url = 'https://www.clinicaltrialsregister.eu/ctr-search/search?query=&page='
    page_html = try_to_connect(5, base_search_url + page)
    output = []
    
    #select all the trial tables
    if page_html:
        trial_tables = page_html.find_all('table', {'class': 'result'})
    
        #get the trial id and the trial url for each thing
        for trial_table in trial_tables:
            trial_id = trial_table.input.get('value')
            #global trial_info
            #trial_ids.append([trial_id])
            country_list = []
            try:
                country_tds = trial_table.find(text="Trial protocol:").parent.parent.find_all('a')
                for c in country_tds:
                    abbrev = c.text.strip()
                    country_list.append(abbrev)
                trial_tuple = (trial_id, country_list)
                output.append(trial_tuple)
            except AttributeError:
                if trial_id == '2008-004625-42':
                    trial_tuple = (trial_id, ['DE'])
                else:
                    trial_tuple = (trial_id, ['Error'])
                output.append(trial_tuple)
        return output
    else:
        pass

if __name__ == '__main__':
    with Pool() as p:
        trial_info = list(tqdm(p.imap(get_trials, pages), total=len(pages)))

tuples = list(trial_info)
tuples = [t for sublist in tuples for t in sublist]

print(f'There are {len(tuples)} trials')

for t in tuples:
    idx = 0
    if 'Error' in t[1]:
        raise ValueError(f'There was an unexpected error in trial {t[0]}')
print('No Trials Had Errors')

sleep(2)

def get_sponsor_info(tup):
    trial_page = 'https://www.clinicaltrialsregister.eu/ctr-search/trial/'
    sects = ['B.1.1', 'B.1.3.4', 'B.3.1 and B.3.2']
    labels = ['sponsor_name', 'sponsor_country', 'sponsor_status']
    prot_dicts = []
    for c in tup[1]:
        trial_dict = {}
        trial_dict['trial_id'] = tup[0]
        if c == 'Outside EU/EEA':
            soup = try_to_connect(5, trial_page + tup[0] + '/' + '3rd')
        else:
            soup = try_to_connect(5, trial_page + tup[0] + '/' + c)
        num_sponsors = soup.find_all(text=re.compile('B.Sponsor:'))
        content_error = soup.find('div', {'class': 'nooutcome'})
        spons_list = []
        if num_sponsors:
            for n_s in num_sponsors:
                a = soup.find(text=n_s).parent.parent.parent
                prot_dict = {}
                prot_dict['protocol_country'] = c
                for s, l in zip(sects, labels):
                    s_text = a.find(text=s).parent.parent.find_all('td')[-1].text.strip()
                    if s_text:
                        prot_dict[l] = s_text
                    else:
                        prot_dict[l] = 'No Data Available'
                spons_list.append(prot_dict)
        else:
            prot_dict = {}
            prot_dict['protocol_country'] = c
            for s,l in zip(sects, labels):
                if content_error:
                    prot_dict[l] = 'Content Generation Error'
                else:
                    prot_dict[l] = 'No Data Available'
            spons_list.append(prot_dict)
        trial_dict['sponsors'] = spons_list
        prot_dicts.append(trial_dict)
    return prot_dicts

if __name__ == '__main__':
	with Pool() as p:
		sponsor_data = list(tqdm(p.imap(get_sponsor_info, tuples), total=len(tuples)))

final_list = list(sponsor_data)
final_list = [fl for sublist in final_list for fl in sublist]

print(f'There were {len(final_list)} protocols scraped')

df = pd.json_normalize(final_list)
s = df['sponsors']
s_exp = pd.concat([pd.DataFrame(x) for x in s], keys = s.index, sort=False)
spons = df.drop('sponsors', 1).join(s_exp.reset_index(level=1, drop=True)).reset_index(drop=True)

end_time = time()

print('Program ran in {} minute(s)'.format(round((end_time - start_time)/60),0))

spons.to_csv('test_spon_info.csv')




