from requests import get
from requests import ConnectionError
from bs4 import BeautifulSoup
import re
from time import time
from time import sleep
import pandas as pd
from multiprocessing import Manager, Pool
from itertools import repeat
#import istarmap
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
#max_page = 50
#chunk1 = [str(i) for i in range(1, 500)]
#chunk2 = [str(i) for i in range(500, 1000)]
#chunk3 = [str(i) for i in range(1000, 1500)]
#chunk4 = [str(i) for i in range(1500, 1784)]
pages = [str(i) for i in range(1,int(max_page)+1)]
#pages = [str(i) for i in range(1,int(max_page)+1)]

manager = Manager()
trial_info = manager.list()

def try_to_connect(tries, url, error_list=None):
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
                print('retry failed')
                if error_list:
                    error_list.append(url)
                page_html = None
    return page_html

def get_trials(pages):
    base_search_url = 'https://www.clinicaltrialsregister.eu/ctr-search/search?query=&page='
    page_html = try_to_connect(5, base_search_url + pages)
    
    #select all the trial tables
    if page_html:
        trial_tables = page_html.find_all('table', {'class': 'result'})
    
        #get the trial id and the trial url for each thing
        for trial_table in trial_tables:
            trial_id = trial_table.input.get('value')
            global trial_info
            #trial_ids.append([trial_id])
            country_list = []
            try:
                country_tds = trial_table.find(text="Trial protocol:").parent.parent.find_all('a')
                for c in country_tds:
                    abbrev = c.text.strip()
                    country_list.append(abbrev)
                trial_tuple = (trial_id, country_list)
                trial_info.append(trial_tuple)
            except AttributeError:
                trial_tuple = (trial_id, ['Error'])
                trial_info.append(trial_tuple)
    else:
        pass

def find_errors(countries, trial_ids):
    idx = 0
    errors = []
    error_trials = []
    for x in countries:
        if x == ['Error']:
            errors.append(idx)
        idx += 1
    print('Error Trials:')
    for e in errors:
        print(trial_ids[e][0])
        error_trials.append(trial_ids[e][0])
    return errors, error_trials

def get_fix(error_trials):
    fixes = []
    for e_t in error_trials:
        fix_input = input('Fix for trial error {}: '.format(e_t))
        list_response = list([fix_input])
        fixes.append(list_response)
    return fixes


def fix_errors(errors, fixes, countries):
    for e, f in zip(errors, fixes):
        countries[e] = f
    return countries

final_list = manager.list()
catch_errors = manager.list()

def get_sponsor_info(trial_ids, countries):
    trial_page = 'https://www.clinicaltrialsregister.eu/ctr-search/trial/'
    sects = ['B.1.1', 'B.1.3.4', 'B.3.1 and B.3.2']
    labels = ['sponsor_name', 'sponsor_country', 'sponsor_status']
    global final_list
    global catch_errors
    for trial, country in zip(repeat(list(trial_ids),len(countries)), countries):
        trial_dict = {}
        trial_dict['trial_id'] = trial[0]
        if country == 'Outside EU/EEA':
            soup = try_to_connect(5, trial_page + trial[0] + '/' + '3rd', error_list=catch_errors)
        else:
            soup = try_to_connect(5, trial_page + trial[0] + '/' + country, error_list=catch_errors)            
        num_sponsors = soup.find_all(text=re.compile('B.Sponsor:'))
        content_error = soup.find('div', {'class': 'nooutcome'})
        spons_list = []        
        if num_sponsors:
            for n_s in num_sponsors:
                a = soup.find(text=n_s).parent.parent.parent 
                prot_dict = {}
                prot_dict['protocol_country'] = country
                for s,l in zip(sects,labels):
                    s_text = a.find(text=s).parent.parent.find_all('td')[-1].text.strip()
                    if s_text:
                        prot_dict[l] = s_text
                    else:
                        prot_dict[l] = 'No Data Available'
                spons_list.append(prot_dict)
        else:
            prot_dict = {}
            prot_dict['protocol_country'] = country
            for s,l in zip(sects, labels):
                if content_error:
                    prot_dict[l] = 'Content Generation Error'
                else:
                    prot_dict[l] = 'No Data Available'
            spons_list.append(prot_dict)
        trial_dict['sponsors'] = spons_list
        final_list.append(trial_dict)

if __name__ == '__main__':
    pool = Pool(8)
    pool.map(get_trials, chunk4)

trial_info = list(trial_info)

print(len(trial_info))

trial_ids = []
countries = []

for t in trial_info:
    trial_ids.append([t[0]])
    countries.append(t[1])

sleep(2)

if ['Error'] in countries:
    errors, error_trials = find_errors(countries, trial_ids)
else:
    errors = []
    print('No Errors')

if errors != []:
    fixes = get_fix(error_trials)
    fix_errors(errors, fixes, countries)
    
sleep(2)

if __name__ == '__main__':
    for _ in tqdm(pool.istarmap(get_sponsor_info, zip(list(trial_ids), list(countries))),
                       total = len(trial_ids)):
        pass
    pool.close()
    pool.join()

len(final_list)

df = pd.io.json.json_normalize(final_list)
s = df['sponsors']
s_exp = pd.concat([pd.DataFrame(x) for x in s], keys = s.index, sort=False)
spons = df.drop('sponsors', 1).join(s_exp.reset_index(level=1, drop=True)).reset_index(drop=True)

end_time = time()

print('Program ran in {} minute(s)'.format(round((end_time - start_time)/60),0))

#def test_single_trial(trial, country):
#    trial_page = 'https://www.clinicaltrialsregister.eu/ctr-search/trial/'
#    sects = ['B.1.1', 'B.1.3.4', 'B.3.1 and B.3.2']
#    labels = ['sponsor_name', 'sponsor_country', 'sponsor_status']
#    trial_dict = {}
#    trial_dict['trial_id'] = trial
#    spons_list = []
#    tries=3
#    for i in range(tries):
#        try:
#            soup = get_url(trial_page + trial + '/' + country)
#            break
#        except ConnectionError as e:
#            if i < tries - 1:
#                sleep(2)
#                continue
#            else:
#                raise e
#    num_sponsors = soup.find_all(text=re.compile('B.Sponsor:'))
#    for n_s in num_sponsors:
#        a = soup.find(text=n_s).parent.parent.parent 
#        prot_dict = {}
#        prot_dict['protocol_country'] = country
#        for s,l in zip(sects,labels):
#            prot_dict[l] = a.find(text=s).parent.parent.find_all('td')[-1].text.strip()
#        spons_list.append(prot_dict)      
#    trial_dict['sponsors'] = spons_list
#    print(trial_dict)