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
import pandas as pd
from time import time
import csv

try:
    get_ipython
    from tqdm.notebook import tqdm
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

trial_list = 'http://rpcec.sld.cu/en/advances-search?page=0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C{}'
pages = list(range(0,16))

hrefs = []
for page in tqdm(pages):
    soup = get_url(trial_list.format(page))
    body = soup.find('tbody').find_all('a')
    for a in body:
        hrefs.append(a.get('href'))

prefix = 'http://registroclinico.sld.cu'
t_list = []
for h in tqdm(hrefs):
    soup = get_url(prefix+h)
    labels = soup.find_all('div', {'class': 'field-label'})
    content = soup.find_all('div', {'class': 'field-items'})
    lab = []
    cont = []
    for l, c in zip(labels,content):
        lab.append(l.text.strip())
        cont.append(c.text.strip())
    t_dict = dict(zip(lab, cont))
    t = h.replace('en/trials', 'ensayos').replace('-En', '-Sp')
    soup2 = get_url(prefix+t)
    if soup2.find('div', text=re.compile('Referencias:')):
        sp_ref = soup2.find('div', text=re.compile('Referencias:')).find_next('div').text.strip()
        t_dict['references_spanish'] = sp_ref
    else:
        pass
    if soup2.find('div', text=re.compile('Resultados:')):
        sp_res = soup2.find('div', text=re.compile('Resultados:')).find_next('div').text.strip()
        t_dict['results_spanish'] = sp_res
    else:
        pass
    t_list.append(t_dict)

import ndjson
with open('rpcec_json.ndjson','w') as r:
    ndjson.dump(t_list, r)


