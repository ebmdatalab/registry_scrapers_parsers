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
from bs4 import BeautifulSoup
import re
from time import time
import csv

try:
    get_ipython
    from tqdm.notebook import tqdm
except NameError:
    from tqdm import tqdm

def get_url(url):
    response = get(url)
    html = response.content
    soup = BeautifulSoup(html, "html.parser")
    return soup

base_url = 'http://lbctr.emro.who.int'

# +
#this is set to 1000 for now as there are only 60 trials on the reigstry, but it appears you can make the pageSize parameter
#as arbitrarily big as you want. Shouldn't need to change for some time though.
#You can also make it one size and iterate over the page paramter.
soup = get_url(base_url + '/Trials/View?Grid-sort=&Grid-page=1&Grid-pageSize=1000&Grid-group=&Grid-filter=')

url_suff = []
for s in soup.find_all('td', {'class':'mbold'}):
    url_suff.append(s.a.get('href'))

# +
trial_info = []

for suff in tqdm(url_suff):
    soup2 = get_url(base_url + suff)
    
    trial_dict = {}
    
    #Getting data from the main table
    main_type_info = soup2.find('div', {'class': 'mainInformation-watermark'})
    data_fields = main_type_info.find_all('label', {'class': 'control-label'})
    idx=0
    for t in data_fields:    
        if not t.attrs['for']:
            continue
        elif t.attrs['for'] and idx == len(data_fields)-1:
            trial_dict[t.text.strip().lower().replace(' ', '_').replace(':','')] = None
        elif t.attrs['for'] and data_fields[idx+1].attrs['for']:
            trial_dict[t.text.strip().lower().replace(' ', '_').replace(':','')] = None
        elif t.attrs['for'] and not data_fields[idx+1].attrs['for']:
            trial_dict[t.text.strip().lower().replace(' ', '_').replace(':','')] = data_fields[idx+1].text.strip()
        idx += 1
    
    #Getting data from everywhere else but results
    
    for tab in soup2.find_all('table'):
        table_name = re.sub(r"(\w)([A-Z])", r"\1 \2", tab.attrs['id'].replace('tbl','')).lower().replace(' ','_')
        table = []
        headers = []
        for h in tab.find_all('th'):
            headers.append(h.text.strip())
        rows = tab.find('tbody').find_all('tr')
        if len(headers) == 1:
            for r in rows:
                for l in r.find_all('label'):
                    table.append(l.text.strip())   
        elif len(headers) > 1 and rows:
            row_dict = {}
            for r in rows:
                data = r.find_all('label')
                for h, d in zip(headers, data):
                    if d:
                        row_dict[h.lower().replace(' ','_')] = d.text.strip()
                    else:
                        row_dict[h.lower().replace(' ','_')] = None
                table.append(row_dict)
        trial_dict[table_name] = table
    
    #Getting data from the Results tab
    
    results_fields = soup2.find('h3', text='Trial Results').find_next('div').find_all('label', {'class': 'control-label'})
    idx=0
    results = {}
    for r in results_fields:
        if not r.attrs['for']:
            continue
        elif r.attrs['for'] and idx == len(results_fields)-1:
            results[r.text.strip().lower().replace(' ', '_').replace(':','')] = None
        elif r.attrs['for'] and results_fields[idx+1].attrs['for']:
            results[r.text.strip().lower().replace(' ', '_').replace(':','')] = None
        elif t.attrs['for'] and not data_fields[idx+1].attrs['for']:
            results[r.text.strip().lower().replace(' ', '_').replace(':','')] = results_fields[idx+1].text.strip()
        idx += 1
    if results:
        trial_dict['trial_results'] = results
    else:
        trial_dict['trial_results'] = None
    
    #appending it all to the master list of trial info
    trial_info.append(trial_dict)
# -

import ndjson
from datetime import date
with open('lbctr_json_{}.ndjson'.format(date.today()),'w') as r:
    ndjson.dump(trial_info, r)


