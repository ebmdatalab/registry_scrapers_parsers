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
#Waiting for the results to load and manually retireving the URL of the last record on the rable

# +
from requests import get
from requests import ConnectionError
from bs4 import BeautifulSoup
import re
from random import randint
from datetime import datetime
from datetime import date
import csv

try:
    get_ipython
    from tqdm import tqdm_notebook as tqdm
except NameError:
    from tqdm import tqdm


# +
def get_html(id):
    url = 'http://ctri.nic.in/Clinicaltrials/pmaindet2.php?trialid={}'.format(id)
    response = get(url, verify = False)
    html = response.content
    soup = BeautifulSoup(html, "html.parser")
    return soup

def get_tables(html):
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
    table_dict = dict(zip(table_names,tables))
    return(table_dict)

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
        fdict[clean_els[i]] = v_type(clean_els[i+1])
    return fdict

def make_date(date):
    if date == "Date Missing" or not date:
        return None
    elif 'Applicable only for' in date:
        return 'Not Applicable'
    else:
        return datetime.strptime(date,'%d/%m/%Y').date()
    
def myconverter(o):
    if isinstance(o, date):
        return o.__str__()

def make_dict():
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
last_trial_id = 33917 #as of 19 May 2019
pages = [str(i) for i in range(1,(last_trial_id+1))]
requests = 0
skipped = 0
written = 0
trial_list = []
test_pages = [str(i) for i in range(1,11)]

with open('ctri_trials.csv', 'w', newline='', encoding='utf-8') as ctri_csv:
    writer = csv.DictWriter(ctri_csv, fieldnames=headers)
    writer.writeheader()
    for page in tqdm(test_pages):
        request +=1
        soup = get_html(page)
        trial_info = get_tables(soup)
        last_td = soup.find_all('td')[-1].text
        if 'Invalid Request!!!' in last_td:
            skipped += 1
            continue
        else:
            t_dict = make_dict()
            written += 1
            writer.writerow(t_dict)


