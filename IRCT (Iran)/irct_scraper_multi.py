from requests import get
from bs4 import BeautifulSoup
import csv
import xmltodict
import re
try:
    get_ipython
    from tqdm.notebook import tqdm
except NameError:
    from tqdm import tqdm
from multiprocessing import Pool
from time import sleep
    
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_xml(num):
    r = get('https://www.irct.ir/trial/{}/xml'.format(num))
    if r.status_code == 404:
        sleep(1)
        return None
    else:
        trial_dict = xmltodict.parse(r.content, dict_constructor=dict)['trials']['trial']
        sleep(1)
        return trial_dict

def get_url(url):
    response = get(url, verify = False)
    html = response.content
    soup = BeautifulSoup(html, "html.parser")
    return soup

search_url = 'https://www.irct.ir/search/result?query=%2A&filters=%7B%22perPage%22%3A%22100%22%2C%22sortBy%22%3A%22relevance%22%2C%22displayFormat%22%3A%22brief%22%2C%22selected%22%3A%5B%5D%7D&page={}'

first_page = get_url(search_url.format(1))
max_trial_count = first_page.find('div', {'class':'result-count'}).find_all('strong')[-1].text.strip()
max_page_count = first_page.find('ul', {'class': 'pagination'}).find_all('li')[-2].text.strip()
pages = list(range(1,int(max_page_count)+1))
#pages = [1,2]

trial_nums = []
for page in tqdm(pages):
    url_ids = get_url(search_url.format(page)) 
    for link_id in soup.find_all('div', {'class': 'result-title'}):
        trial_nums.append(re.findall(digits, link_id.a.get('href'))[0])

if __name__ == '__main__':
	with Pool() as p:
		trials = list(tqdm(p.imap(get_xml, trial_nums), total=len(trial_nums)))

trial_dicts = list(trials)
only_trials = [i for i in trial_dicts if i]

all_keys = set().union(*(t.keys() for t in only_trials))
labels = list(all_keys)

from datetime import date
import csv

def irct_csv():
    with open('irct - ' + str(date.today()) + '.csv','w', newline = '', encoding='utf-8') as irct_csv:
        writer=csv.DictWriter(irct_csv,fieldnames=labels)
        writer.writeheader()
        writer.writerows(only_trials)

irct_csv()