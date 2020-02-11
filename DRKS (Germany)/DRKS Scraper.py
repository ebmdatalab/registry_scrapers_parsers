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


# +
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from time import sleep
import os
import re
from requests import get
from bs4 import BeautifulSoup
from pathlib import Path
import platform

platform = platform.platform()
cwd = os.getcwd()
download_path = os.path.join(cwd,'CRiS Downloads')
#adjust this to fit your specific file structure 
parent = str(Path(cwd).parents[0]) 

if "Darwin" in platform:
    chrome_driver = os.path.join(parent, 'Drivers', 'chromedriver')
elif "Windows" in platform:
    chrome_driver = os.path.join(parent, 'Drivers', 'chromedriver.exe')
else:
    print("No OS/Chromedriver match. OS: {}".format(platform))

# +
#Pull the last trial ID using Selenium

chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory" : download_path,
        'disk-cache-size': 4096,
        'safebrowsing.enabled': 'false'}
chromeOptions.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(executable_path=chrome_driver, options=chromeOptions)
driver.get('https://www.drks.de/drks_web/setPage.do?page=1')
select = Select(driver.find_element_by_name('criteria.sortField'))
select.select_by_value('trial_drks_id')
driver.find_element_by_xpath("//a[@href ='setPage.do?page=last']").click()
thing = (driver.find_element_by_xpath("//tbody")).text
driver.quit()

split = thing.split('|')
last_id = re.findall(re.compile('DRKS\d{8}'), split[-1])[0]

#Then go an make a list of all possibl trial IDs from 1 to the max

last_n = int(last_id[-5:])

id_num_list = list(range(1,last_n+1))

trial_ids = []
for num in id_num_list:
    trial_id = 'DRKS' + '0' * (8 - len(str(num))) + str(num)
    trial_ids.append(trial_id)
# -

print(last_n)


# +
#all functions to proccess data

def does_it_exist(soup, element, e_class, n_e=False):
    if not n_e:
        location = soup.find(element, class_=e_class).text.strip()
    elif n_e:
        location = soup.find(element, class_=e_class).next_element.next_element.next_element.next_element.strip()
    if location == '[---]*':
        field = None
    else:
        field = location
    return field

def get_contact_info(soup, address_num):

    test_dict = {}

    addresses = soup.find_all('ul', class_='trial_address')
    if address_num > len(addresses)-1:
        test_dict = None
    else:
        uls = addresses[address_num].find_all('li')
        counter = 1
        ad_str = ''
        for u in uls:
            u = u.text.strip()
            u = re.sub('\s+', ' ', u)
            if counter < len(uls):
                ad_str = ad_str + u + " "
            else:
                as_str = ad_str + u

        test_dict['sponsor_address'] = ad_str

        a_labels = ['phone', 'fax', 'email', 'url']
        contacts = soup.find_all('ul', class_='trial_address_contact')
        ul = contacts[address_num].find_all('li')
        for u, l in zip(ul, a_labels):
            li_t = u.text.strip()
            li_t = re.sub('\s+', '', li_t)
            if 'URL:' in li_t:
                li_list = li_t.split('RL:')
            else:
                li_list = li_t.split(':')
            if li_list[1] == '[---]*':
                test_dict[l] = None
            else:
                test_dict[l] = li_list[1]
    return test_dict

def trial_info(soup):    
    t_d = {}

    t_d['drks_id'] = soup.find('li', class_='drksId').next_element.next_element.next_element.next_element.strip()

    if soup.find('div', class_='retrospective-hint'):
        t_d['registration_status'] = 'retrospective'
    else:
        t_d['registration_status'] = 'prospetive'

    st_class = ['state', 'deadline']
    st_labels = ['recruitment_status', 'study_closing_date']
    for lab, s_class in zip(st_labels, st_class):
        t_d[lab] = does_it_exist(soup, 'li', s_class, n_e=True)

    t_d['trial_acronym'] = does_it_exist(soup, 'p', 'acronym')
    t_d['trial_url'] = does_it_exist(soup, 'p', 'trial_url')
    t_d['registration_date'] = does_it_exist(soup, 'li', 'firstDrksPublishDate', n_e = True)
    t_d['partner_registration_date'] = does_it_exist(soup, 'li', 'firstPartnerPublishDate', n_e = True)
    t_d['investigator_sponsored_or_initiated_trial'] = does_it_exist(soup, 'li', 'investorInitiated', n_e = True)
    t_d['ethics_info'] = {'ethics_status': does_it_exist(soup, 'li', 'ethicCommitteeVote', n_e=True),
                          'ethics_committee': does_it_exist(soup, 'li', 'ethicCommissionNumber', n_e=True)}

    s_id_list = []
    ul = soup.find('ul', class_='secondaryIDs').find_all('li')
    if ul[0].text == '[---]*':
        s_id_list = None
    else:
        for u in ul:
            s_id_dict = {}
            s_id_dict['id_type'] = u.next_element.next_element.next_element.strip().replace(':','')
            li_t = u.next_element.next_element.next_element.next_element.strip()
            li_t = re.sub('\n', '|', li_t)
            li_t = re.sub('\s+', '', li_t).replace('(','').replace(')','')
            id_info = li_t.split('|')
            if len(id_info) > 1:   
                s_id_dict['registry'] = id_info[1]
                s_id_dict['secondary_id'] = id_info[0]
            else:
                s_id_dict['registry'] = None
                s_id_dict['secondary_id'] = id_info[0]
            s_id_list.append(s_id_dict)
    t_d['secondary_ids'] = s_id_list

    h_list = []
    ul = soup.find('ul', class_='health-conditions').find_all('li')
    if ul[0].text == '[---]*':
        h_list = None
    else:
        for u in ul:
            h_dict = {}
            h_dict['identifier_type'] = u.next_element.next_element.next_element.strip().replace(':','')
            li_t = u.next_element.next_element.next_element.next_element.strip()
            li_t = re.sub('\s+', '', li_t)
            h_dict['condition'] = li_t
            h_list.append(h_dict)
    t_d['health_condition_problem'] = h_list 

    i_list = []
    ul = soup.find('ul', class_='interventions').find_all('li')
    if ul[0].text == '[---]*':
        i_list = None
    else:
        for u in ul:
            i_dict = {}
            i_dict['arm'] = u.next_element.next_element.next_element.strip().replace(':','')
            li_t = u.next_element.next_element.next_element.next_element.strip()
            i_dict['intervention_type'] = li_t
            i_list.append(i_dict)
    t_d['interventions'] = i_list

    char_class = ['type', 'typeNotInterventional', 'allocation', 'masking maskingType', 'maskingWho', 'control', 'purpose',
                  'assignment', 'phase', 'offLabelDrugUse']
    char_labels = ['study_type', 'study_type_non_int', 'allocation', 'blinding', 'who_blinded', 'control', 'purpose', 
                  'assignemnt', 'phase', 'off_label_drug']
    char_dict = {}
    for lab, c_class in zip(char_labels, char_class):
        char_dict[lab] = does_it_exist(soup, 'li', c_class, n_e=True)
    t_d['trial_charcteristics'] = char_dict

    t_d['primary_outcomes'] = does_it_exist(soup, 'p', 'primaryEndpoint')

    t_d['secondary_outcomes'] = does_it_exist(soup, 'p', 'secondaryEndpoints')

    c_list = []
    ul = soup.find('ul', class_='recruitmentCountries').find_all('li')
    if ul[0].text == '[---]*':
        c_list = None
    else:
        for u in ul:
            li_t = u.text.strip()
            li_t = re.sub('\s+', '', li_t)
            li_list = li_t.split(':')
        c_list.append(li_list[1])
    t_d['countries'] = c_list

    l_list = []
    ul = soup.find('ul', class_='recruitmentLocations').find_all('li')
    if ul[0].text == '[---]*':
        l_list = None
    else:
        for u in ul:
            l_dict = {}
            loc = u.next_element.next_element.text.strip()
            loc = re.sub('\s+', '', loc).replace(',', ', ')
            l_dict['location'] = loc
            l_dict['location_type'] = ul[0].next_element.strip()
            l_list.append(l_dict)
    t_d['recuitment_locations'] = l_list

    rec_class = ['running', 'schedule', 'targetSize', 'monocenter', 'national']
    rec_labels = ['planned_actual', 'date_of_first_enrollment', 'target_sample_size', 'mono_multi_center', 
                  'national_international']
    rec_dict = {}
    for lab, r_class in zip(rec_labels, rec_class):
        rec_dict[lab] = does_it_exist(soup, 'li', r_class, n_e=True)
    t_d['recruitment_info'] = rec_dict

    inc_class = ['gender', 'minAge', 'maxAge']
    inc_labels = ['gender', 'min_age', 'max_age']
    inc_dict = {}
    for lab, i_class in zip(inc_labels, inc_class):
        inc_dict[lab] = does_it_exist(soup, 'li', i_class, n_e=True)
    t_d['inclusion_criteria'] = rec_dict

    t_d['additional_inclusion_criteria'] = does_it_exist(soup, 'p', 'inclusionAdd')

    t_d['exclusion_criteria'] = does_it_exist(soup, 'p', 'publicSummary')

    t_d['lay_summary'] = does_it_exist(soup, 'p', 'exclusion')

    t_d['scientific_summary'] = does_it_exist(soup, 'p', 'scientificSynopsis')

    t_d['primary_sponsor_contact'] = get_contact_info(soup, 0)

    t_d['scientific_contact'] = get_contact_info(soup, 1)

    t_d['public_contact'] = get_contact_info(soup, 2)

    t_d['funder_contact'] = get_contact_info(soup, 3)

    docs_list = []
    ul = soup.find('ul', class_='publications').find_all('li')
    if ul[0].text == '[---]*':
        docs_list = None
    else:
        for u in ul:
            doc_dict = {}
            doc_dict['document_type'] = u.next_element.next_element.next_element.strip().replace(':','')
            if u.find('a'):
                doc_dict['link_to_document'] = u.find('a').get('href')
            else:
                doc_dict['link_to_document'] = None
            docs_list.append(doc_dict)
    t_d['results_publications_documents'] = docs_list

    return t_d


# +
base_url = 'https://www.drks.de/drks_web/navigate.do?navigationId=trial.HTML&TRIAL_ID='

error_text = ['Due to an error of the data management, this study was inadvertently registered incompletely.',
              'This study has been imported from ClinicalTrials.gov inadvertently, although it had been registered with DRKS before.']

headers = ['drks_id', 'registration_status', 'recruitment_status', 'study_closing_date', 'trial_acronym', 'trial_url',
 'registration_date', 'partner_registration_date', 'investigator_sponsored_or_initiated_trial', 'ethics_info', 'secondary_ids',
 'health_condition_problem', 'interventions', 'trial_charcteristics', 'primary_outcomes', 'secondary_outcomes', 'countries',
 'recuitment_locations', 'recruitment_info', 'inclusion_criteria', 'additional_inclusion_criteria', 'exclusion_criteria',
 'lay_summary', 'scientific_summary', 'primary_sponsor_contact', 'scientific_contact', 'public_contact', 'funder_contact',
 'results_publications_documents']
# -

start_time = time()
with open('drks_trials.csv', 'w', newline='', encoding='utf-8') as drks_csv:
    writer = csv.DictWriter(drks_csv, fieldnames=headers)
    writer.writeheader()
    for tid in tqdm(trial_ids[]):
        soup = get_url(base_url + tid)
        if soup.find('ul', {'class':'errors'}) or soup.find('div', class_='trial').text in error_text:
            pass
        else:
            try:
                writer.writerow(trial_info(soup))
            except Exception as e:
                import sys
                raise type(e)(str(e) + '\n' + 'Error trial: {}'.format(tid)).with_traceback(sys.exc_info()[2])
end_time = time()
print('Scrape Finished in {} minues'.format(round((end_time-start_time) / 60),0))


