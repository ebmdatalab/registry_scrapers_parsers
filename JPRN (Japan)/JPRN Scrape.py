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
from requests import get
from requests import ConnectionError
from bs4 import BeautifulSoup
import re
import pandas as pd
from time import time
import csv

try:
    get_ipython
    from tqdm import tqdm_notebook as tqdm
except NameError:
    from tqdm import tqdm
    
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
def get_url(url):
    response = get(url, verify = False)
    html = response.content
    soup = BeautifulSoup(html, "html.parser")
    return soup


# -

soup = get_url('https://rctportal.niph.go.jp/en/result?t=chiken&l=50&s=0')

trial_count = soup.find('div', {'id': 'result-counts'}).find('span').text

start_time = time()
all_links = []
#pages = list(range(0,int(trial_count)+1,50))
pages = list(range(0,400+1,50))
for p in tqdm(pages):
    soup = get_url('https://rctportal.niph.go.jp/en/result?t=chiken&l=50&s={}'.format(str(p)))
    hrefs = soup.find('div', {'class': 'chikentbl'}).find_all('a')
    hrefs = hrefs[10:]
    for h in hrefs:
        all_links.append(h.get('href'))
end_time = time()
print('Scrape Finished in {} minues'.format(round((end_time-start_time) / 60),0))

# +
jprn_prefix = 'https://rctportal.niph.go.jp'

def get_field(soup, field):
    x = soup.find(text=field).parent.parent.find('td').text
    return x

def get_table(soup, table, t_dict):
    tab = soup.find('table', {'class': table}).find_all('th')
    for t in tab:
        t_dict[t.text.lower().replace(' ','_')] = get_field(soup, t.text)

def get_common(table, soup):
    temp_dict = {}
    fields = table.find_all('th')
    for f in fields:
        temp_dict[f.text.lower().replace(' ','_')] = get_field(soup, f.text)
    return temp_dict

def get_row(soup):
    t_d = {}
    t_d['trial_id'] = re.search(r":\s(.*)", soup.find('div', {'class': 'japicid'}).text).group(1)
    t_d['registered_date'] = re.search(r":\s?(.*)", soup.find('div', {'class': 'signupdate'}).text).group(1)
    get_table(soup, 'basic', t_d)
    t_d['original_registry_link'] = soup.find('div', {'class','syousaibtn'}).find('a').get('rel')[0]
    get_table(soup, 'test', t_d)
    get_table(soup, 'target', t_d)
    tables = soup.find_all('table', {'class': 'common'})
    t_d['sponsor_info'] = get_common(tables[0], soup)
    ids_field = tables[1].find('th').parent.parent.find('td')
    if ',' in ids_field:
        t_d['secondary_ids'] = ids_field.text.split(',')
    else:
        t_d['secondary_ids'] = ids_field.text

    c1 = tables[2].find_all('tr')[1:6]
    c2 = tables[2].find_all('tr')[7:]
    contact_fields = ['name', 'address', 'telephone', 'email', 'affiliation']

    public_contact = {}
    for c, cf in zip(c1, contact_fields):
        public_contact[cf] = c.find_all('td')[1].text
    t_d['public_contact'] = public_contact

    scientific_contact = {}
    for c, cf in zip(c2, contact_fields):
        scientific_contact[cf] = c.find_all('td')[1].text
    t_d['scientific_contact'] = scientific_contact
    
    t_d['ethics_info'] = get_common(tables[3], soup)
    t_d['results_info'] = get_common(tables[4], soup)
    t_d['ipd_sharing'] = get_common(tables[5], soup)
    return t_d

headers = ['trial_id', 'registered_date', 'public_title', 'scientific_title', 'recruitment_status', 
           'health_condition(s)_or_problem(s)_studied', 'study_type', 'phase', 'study_design', 'intervention(s)', 
           'sample_size', 'date_of_first_enrollment', 'completion_date', 'countries_of_recruitment', 'original_registry_link',
           'primary_outcome', 'secondary_outcome', 'age_minimum', 'age_maximum', 'gender', 'include_criteria',
           'exclude_criteria', 'sponsor_info', 'secondary_ids', 'public_contact', 'scientific_contact', 'ethics_info',
           'results_info', 'ipd_sharing']
# -

start_time = time()
with open('jprn_trials.csv', 'w', newline='', encoding='utf-8') as jprn_csv:
    writer = csv.DictWriter(jprn_csv, fieldnames=headers)
    writer.writeheader()
    request = 0
    for l in tqdm(all_links):
        soup = get_url(jprn_prefix + l)
        trial_info = get_row(soup)
        writer.writerow(trial_info)
end_time = time()
print('Scrape Finished in {} minues'.format(round((end_time-start_time) / 60),0))

# +
#https://stackoverflow.com/questions/43842206/how-to-filter-a-pandas-dataframe-by-dict-column
