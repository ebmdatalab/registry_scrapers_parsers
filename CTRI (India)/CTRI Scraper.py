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

# # CTRI

# +
#There is not a simple way to get the current max trial ID via code.
#This needs to be retrieved manually by:
#Visting the CTRI
#Doing the broadest possible search (i.e. searching for the letter 'a')
#Waiting for the results to load and manually retireving the URL of the last record on the table

# +
from requests import get
from requests import ConnectionError
from bs4 import BeautifulSoup
import re
from random import randint
from datetime import datetime
from datetime import date
import csv
from time import sleep

try:
    get_ipython
    from tqdm.notebook import tqdm
except NameError:
    from tqdm import tqdm


# +
def get_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    tries=3
    for i in range(tries):
        try:
            response = get(url, verify = False, headers=headers)
        except ConnectionError as e:
            if i < tries - 1:
                sleep(2)
                continue
            else:
                raise
    html = response.content
    soup = BeautifulSoup(html, "html.parser")
    return soup

def get_tables(html): #It's too unpredictable which tables can be missing from a record. This probably needs
    #Some kind of validation by the text in the table to what should be in the table
    #For instance this http://ctri.nic.in/Clinicaltrials/pmaindet2.php?trialid=788 breaks our fix for trial 184
    tables = html.find_all('table')
    table_names = [
        'all',
        'header',
        'cont1',
        'ids',
        'pi',
        'sci_con',
        'pub_con',
        'mon_sup',
        'p_spon',
        's_spon',
        'sites',
        'ethics',
        'reg',
        'conds',
        'ints',
        'inc_c',
        'ex_c',
        'p_out',
        's_out'
    ]
    if len(tables) == len(table_names):
        table_dict = dict(zip(table_names,tables))
    elif len(tables) < len(table_names) and len(tables) > 0:
        #for now it seems like ids is the only table that can be missing
        #for example http://ctri.nic.in/Clinicaltrials/pmaindet2.php?trialid=184
        table_names.remove('ids')
        table_dict = dict(zip(table_names, tables))
    elif len(tables) > len(table_names):
        #this deals with when an extra table is thrown in within the results section
        #here: http://ctri.nic.in/Clinicaltrials/pmaindet2.php?trialid=719
        tables = tables[0:-1]
        table_dict = dict(zip(table_names, tables))
    else:
        return None
    return table_dict

headers = [
    'ctri_number',
    'registration_date',
    'registration_type',
    'last_modified',
    'post_grad_thesis',
    'type_of_trial',
    'type_of_study',
    'study_design',
    'public_title_of_study',
    'scientific_title_of_study',
    'secondary_id',
    'pi_info',
    'scientific_contact',
    'public_contact',
    'sources_of_monetary_or_material_support',
    'primary_sponsor',
    'secondary_sponsor',
    'recruitment_countries',
    'number_of_sites',
    'study_sites',
    'ethics_details',
    'dcgi_reg_status',
    'conditions_studied',
    'intervention',
    'inclusion_criteria',
    'exclusion_criteria',
    'method_rand_seq',
    'concealment_method',
    'blinding_masking',
    'primary_outcomes',
    'secondary_outcomes',
    'target_sample_size',
    'phase',
    'date_of_first_enrollment_india',
    'date_of_study_completion_india',
    'date_of_first_enrollment_global',
    'date_of_study_completion_global',
    'estimated_duration',
    'recruitment_status_global',
    'recruitment_status_india',
    'publication_details',
    'brief_summary'
]

def get_changes(page, blid):
    change_dates = []
    change_log = get_url('http://ctri.nic.in/Clinicaltrials/pviewmod.php?trialid={}&blid={}&EncHid=&modid=&compid='.format(page, blid))
    changes = change_log.find_all('td', text=re.compile('^\d{2}/\d{2}/\d{4}$'))
    if changes:
        for c in changes:
            change_dates.append(c.text)
        return change_dates
    else:
        return None


# +
reg_date = re.compile(r'\d{2}/\d{2}/\d{4}\b')
digits = re.compile(r'\b\d{1,3}\b')

def strip_chars(text):
    return text.replace('\t',' ').replace('\n',' ').replace('\r',' ').replace('\xa0',' ')

def reg_type():
    c_font = trial_info['cont1'].find_all('font')[0].get_text()
    if 'Trial Registered' in c_font:
        return c_font
    else:
        return None

def text_strip(table, index):
    tds = trial_info[table].find_all('td')
    return strip_chars(tds[index].text.strip())

def tables(cols, column_names, tab_name, extra_row = False):
    counter = 0
    table_contents = []
    t = trial_info[tab_name].find_all('td')
    tab_values = list(range(cols,len(t)))
    rows = list(range(cols,len(t),cols))
    if extra_row:
        tab_values = list(range(cols+1,len(t)))
        rows = list(range(cols+1,len(t),cols))
    counter = 0
    for row in rows:
        d = {}
        for name, v in zip(column_names, tab_values[counter:row]):
            if t[v].text.strip() == 'NIL' or t[v].text.strip() == None:
                d[name] = None
            else:
                d[name] = strip_chars(t[v].text.strip())
        counter += cols
        table_contents.append(d)                
    if len(table_contents) == 1 and (not all(table_contents[0].values())):
        return(None)
    elif len(table_contents) == 1 and (all(table_contents[0].values())):
        return(table_contents[0])
    elif len(table_contents) > 1:
        return(table_contents)
    else:
        return(None)

def bare_table(table):
    contact_info = {}
    for tr in trial_info[table].find_all('tr'):
        key = tr.find_all('td')[0].text.strip()
        value = strip_chars(tr.find_all('td')[1].text.strip())
        contact_info[key.replace(' ','_').lower()] = value
    if not all(contact_info.values()):
        return None
    else:
        return contact_info

def countries():
    tds = trial_info['cont1'].find_all('td')
    index = -1
    for td in tds:
        index += 1
        if td.find(text='Countries of Recruitment'):
            i = index
            break
    locs = list(tds[i+1].stripped_strings)
    if len(locs) == 1:
        return locs[0]
    else:
        return locs

def bare_text(field, table, find_index=False):
    tds = trial_info[table].find_all('td')
    index = -1
    for td in tds:
        index += 1
        if td.find(text = field):
            i = index
            break
    if find_index:
        return i
    elif not find_index:
        return strip_chars(tds[i+1].text.strip())
    
def list_of_fields(td, v_type=str):
    els = list(td.stripped_strings)
    clean_els = []
    for el in els:
        stripped = strip_chars(el.strip().replace('=','').replace('"','').replace(' ','_').lower())
        clean_els.append(stripped)
    key_i = list(range(0,len(els),2))
    fdict = {}
    for i in key_i:
        if clean_els[i+1] == '':
            fdict[clean_els[i]] = None
        else:
            fdict[clean_els[i]] = v_type(clean_els[i+1])
    return fdict

def make_date(date):
    if date == "Date Missing" or date == '00/00/0000' or not date:
        return None
    elif 'Applicable only for' in date:
        return 'Not Applicable'
    else:
        return datetime.strptime(date,'%d/%m/%Y').date()
    
def myconverter(o):
    if isinstance(o, date):
        return o.__str__()

#This is an attempt at scraping every field on the registry. It currently is not 100% functional across all fields.
#Below we make a new function that shortens this to only what is needed for our project on registry results.
#Can come back to in the future and try and fix.
def make_dict(trial_info):
    trial_dict = {}
    trial_dict['ctri_number'] = trial_info['cont1'].find_all('b')[1].text.strip()
    trial_dict['registration_date'] = reg_date.findall(str(trial_info['cont1']))[0]
    trial_dict['registration_type'] = reg_type()
    trial_dict['last_modified'] = text_strip('cont1',3)
    trial_dict['post_grad_thesis'] = text_strip('cont1',5)
    trial_dict['type_of_trial'] = text_strip('cont1',7) 
    trial_dict['type_of_study'] = text_strip('cont1',9) 
    trial_dict['study_design'] = text_strip('cont1',11) 
    trial_dict['public_title_of_study'] = text_strip('cont1',13) 
    trial_dict['scientific_title_of_study'] = text_strip('cont1',15)
    if 'id' in trial_info:
        id_names = ['id', 'identifier_type']
        trial_dict['secondary_id'] = tables(2, id_names, 'ids')
    trial_dict['pi_info'] = bare_table('pi')
    trial_dict['scientific_contact'] = bare_table('sci_con')
    trial_dict['public_contact'] = bare_table('pub_con')
    trial_dict['sources_of_monetary_or_material_support'] = text_strip('mon_sup', 0)
    trial_dict['primary_sponsor'] = bare_table('p_spon')
    spon_cols = ['name', 'address']
    trial_dict['secondary_sponsor'] = tables(2, spon_cols, 's_spon')
    trial_dict['recruitment_countries'] = countries()
    trial_dict['number_of_sites'] = int(digits.findall(trial_info['sites'].td.text.strip())[0])
    sites_cols = ['pi', 'site_name', 'site_address', 'site_contact']
    trial_dict['study_sites'] = tables(4,sites_cols,'sites',extra_row = True)
    ethics_cols = ['committee', 'status']
    trial_dict['ethics_details'] = tables(2,ethics_cols,'ethics',extra_row = True)
    trial_dict['dcgi_reg_status'] = trial_info['reg'].find_all('td')[1].text.strip()
    cond_cols = ['health_type','conditions']
    trial_dict['conditions_studied'] = tables(2,cond_cols,'conds')
    int_cols = ['type', 'name', 'details']
    trial_dict['intervention'] = tables(3, int_cols, 'ints')
    trial_dict['inclusion_criteria'] = bare_table('inc_c')
    trial_dict['exclusion_criteria'] = trial_info['ex_c'].find_all('td')[1].text.strip()
    trial_dict['method_rand_seq'] = bare_text('Method of Generating Random Sequence', 'cont1')
    trial_dict['concealment_method'] = bare_text('Method of Concealment', 'cont1')
    trial_dict['blinding_masking'] = bare_text('Blinding/Masking', 'cont1')
    outcome_cols = ['outcomes', 'timepoint']
    trial_dict['primary_outcomes'] = tables(2,outcome_cols,'p_out')
    trial_dict['secondary_outcomes'] = tables(2,outcome_cols,'s_out')
    enrollment = trial_info['cont1'].find_all('td')[-1]
    trial_dict['target_sample_size'] = list_of_fields(enrollment)
    trial_dict['phase'] = bare_text('Phase of Trial','all')
    trial_dict['date_of_first_enrollment_india'] = make_date(bare_text('Date of First Enrollment (India)','all'))
    trial_dict['date_of_study_completion_india'] = make_date(bare_text('Date of Study Completion (India)','all'))
    trial_dict['date_of_first_enrollment_global'] = make_date(bare_text('Date of First Enrollment (Global)','all'))
    trial_dict['date_of_study_completion_global'] = make_date(bare_text('Date of Study Completion (Global)','all'))
    duration_index = bare_text('Estimated Duration of Trial', 'all', find_index=True)
    duration = trial_info['all'].find_all('td')[duration_index+1]
    trial_dict['estimated_duration'] = list_of_fields(duration, v_type=int)
    trial_dict['recruitment_status_global'] = bare_text('Recruitment Status of Trial (Global)', 'all')
    trial_dict['recruitment_status_india'] = bare_text('Recruitment Status of Trial (India)', 'all')
    trial_dict['publication_details'] = bare_text('Publication Details', 'all')
    trial_dict['brief_summary'] = bare_text('Brief Summary','all')
    return trial_dict


# -

request = 0
last_trial_id = 40107 #as of 25 Jan 2020
pages = [str(i) for i in range(1,(last_trial_id+1))]
requests = 0
skipped = 0
written = 0
url = 'http://ctri.nic.in/Clinicaltrials/pmaindet2.php?trialid={}'
pub_results_changed = []
bsum_results_changed = []
trials = []
#test_pages = [str(i) for i in range(1,100)]

# +
#Only the fields we need for our current analysis

def just_results(trial_info):
    trial_dict = {}
    trial_dict['ctri_number'] = trial_info['cont1'].find_all('b')[1].text.strip()
    trial_dict['registration_date'] = reg_date.findall(str(trial_info['cont1']))[0]
    trial_dict['registration_type'] = reg_type()
    trial_dict['type_of_trial'] = text_strip('cont1',7)
    trial_dict['public_title_of_study'] = text_strip('cont1',13)
    trial_dict['phase'] = bare_text('Phase of Trial','all')
    trial_dict['date_of_first_enrollment_india'] = make_date(bare_text('Date of First Enrollment (India)','all'))
    trial_dict['date_of_study_completion_india'] = make_date(bare_text('Date of Study Completion (India)','all'))
    trial_dict['date_of_first_enrollment_global'] = make_date(bare_text('Date of First Enrollment (Global)','all'))
    trial_dict['date_of_study_completion_global'] = make_date(bare_text('Date of Study Completion (Global)','all'))
    trial_dict['recruitment_status_global'] = bare_text('Recruitment Status of Trial (Global)', 'all')
    trial_dict['recruitment_status_india'] = bare_text('Recruitment Status of Trial (India)', 'all')
    trial_dict['publication_details'] = bare_text('Publication Details', 'all')
    #Brief Summaries are now excluded from the scrape as they are often large and unweildy and can break the resulting CSV
    #trial_dict['brief_summary'] = bare_text('Brief Summary','all')
    return trial_dict


# +
#Scraping is a bit slow moving here. You might have it break for Timeout reasons in which case you can just restart and 
#slice the pages list from where it broke. So if it broke on trial 1400, add [1400:] to the end of `pages` in `tqdm(pages)`
#We also scrape the "Changes" section to the publication and brief summary fields 
#for our project

for page in tqdm(pages):
    requests += 1
    soup = get_url(url.format(page))
    trial_info = get_tables(soup)
    last_td = soup.find_all('td')[-1].text
    if 'Invalid Request!!!' in last_td:
        skipped += 1
        continue
    else:
        t_dict = just_results(trial_info)
        trials.append(t_dict)
        pub_changes = get_changes(page, 29)
        pc_dict = {}
        if pub_changes:
            pc_dict['ctri_number'] = t_dict['ctri_number']
            pc_dict['pub_changes'] = pub_changes
            pub_results_changed.append(pc_dict)
        bsum_changes = get_changes(page, 28)
        bc_dict = {}
        if bsum_changes:
            bc_dict['ctri_number'] = t_dict['ctri_number']
            bc_dict['bsum_changes'] = bsum_changes
            bsum_results_changed.append(bc_dict)

# +
simple_headers = ['ctri_number', 'registration_date', 'registration_type', 'type_of_trial', 'public_title_of_study', 
                  'phase', 'date_of_first_enrollment_india', 'date_of_study_completion_india', 
                  'date_of_first_enrollment_global', 'date_of_study_completion_global', 'recruitment_status_global', 
                  'recruitment_status_india', 'publication_details']

with open('ctri_trials_{}.csv'.format(date.today()), 'w', newline='', encoding='utf-8') as ctri_csv:
    writer = csv.DictWriter(ctri_csv, fieldnames=simple_headers)
    writer.writeheader()
    for t in trials:
        writer.writerow(t)

# +
#This is me being lazy

import pandas as pd

p_changes = pd.DataFrame(pub_results_changed)
p_changes.to_csv('pub_results_changes_{}.csv'.format(date.today()))

b_changes = pd.DataFrame(bsum_results_changed)
b_changes.to_csv('bsum_results_changes_{}.csv'.format(date.today()))
# -

