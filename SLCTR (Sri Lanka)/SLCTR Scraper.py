# -*- coding: utf-8 -*-
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


# +
search_urls = 'https://slctr.lk/trials/search?page={}&s=&type=by_pt'

soup = get_url('https://slctr.lk/trials/search?page=1&s=&type=by_pt')

# +
max_page = soup.find('div', {'class':'pagination'}).find_all('li')[-2].text

page_list = list(range(1,int(max_page)+1))

# +
id_list = []
for page in tqdm(page_list):
    soup = get_url(search_urls.format(page))
    td_list = soup.find('table', {'class', 'table table-striped'}).find_all('td', text=re.compile('^SLCTR'))
    for td in td_list:
        tid = td.text
        id_list.append(tid.replace('/','-'))

base_trial_urls = 'https://slctr.lk/trials/'


# +
def normal_field(soup, field_name):
    return soup.find('p', text=field_name).findNext('p').text.strip()

def get_row(soup):
    t_d = {}
    t_d['trial_id'] = normal_field(soup, 'SLCTR Registration Number')
    t_d['trial_title'] = soup.find('h2', {'class': 'trial-title'}).text.replace('\n- ','')
    t_d['registration_date'] = soup.find('p', text='Date of Registration').findNext('div').text.strip()
    t_d['last_updated_date'] = soup.find('p', text='The date of last modification').findNext('div').text.strip()
    t_d['scientific_title'] = soup.find('p', text='Scientific Title of Trial').findNext('p').findNext('p').text

    t_d['public_title'] = normal_field(soup, 'Public Title of Trial')
    t_d['brief_title'] = normal_field(soup, 'Brief title')
    t_d['study_disease_condition'] = normal_field(soup, 'Disease or Health Condition(s) Studied')

    t_d['scientific_acronym'] = normal_field(soup, 'Scientific Acronym')
    t_d['public_acronym'] = normal_field(soup, 'Public Acronym')
    t_d['universal_trial_number'] = normal_field(soup, 'Universal Trial Number')
    t_d['other_trial_ids'] = normal_field(soup,'Any other number(s) assigned to the trial and issuing authority')
    t_d['research_question'] = normal_field(soup,'What is the research question being addressed?')
    t_d['study_type'] = normal_field(soup,'Type of study')
    t_d['allocation'] = normal_field(soup,'Allocation')
    masking = normal_field(soup,'Masking')
    t_d['masking'] = " ".join(masking.split())
    t_d['control'] = normal_field(soup,'Control')
    t_d['assignment'] = normal_field(soup,'Assignment')
    t_d['purpose'] = normal_field(soup,'Purpose')
    t_d['phase'] = normal_field(soup,'Study Phase')
    t_d['planned_intervention'] = normal_field(soup,'Intervention(s) planned')
    t_d['inclusion_criteria'] = soup.find('p', text='Inclusion criteria').findNext('div').text.strip().replace('•','').replace(' – ','-')
    t_d['exclusion_criteria'] = soup.find('p', text='Exclusion criteria').findNext('div').text.strip().replace('•','').replace(' – ','-')

    outcomes = soup.find('p', text='Primary outcome(s)').findNext('div').table.find_all('div', {'class':'outcome-block'})
    timeframes = soup.find('p', text='Primary outcome(s)').findNext('div').table.find_all('em', {'class':'custom-inline'})
    pat = re.compile(r'^\d{1,2}.?\s$')

    outcome_list = []
    for o, t in zip(outcomes, timeframes):
        outcome_dict = {}
        if not pat.match(o.text) and t.text != '[]':
            outcome_dict['outcome'] = o.text.strip().replace('\n','')
            outcome_dict['timeframe'] = t.text.strip().replace('\n','').replace('[','').replace(']','')
            outcome_list.append(outcome_dict)
        elif pat.match(o.text) and t.text != '[]':
            outcome_dict['outcome'] = None
            outcome_dict['timeframe'] = t.text.strip().replace('\n','').replace('[','').replace(']','')
            outcome_list.append(outcome_dict)
        elif not pat.match(o.text) and t.text == '[]': 
            outcome_dict['outcome'] = o.text.strip().replace('\n','')
            outcome_dict['timeframe'] = None
            outcome_list.append(outcome_dict)
        else:
            pass
    t_d['primary_outcomes'] = outcome_list

    s_outcomes = soup.find('p', text='Secondary outcome(s)').findNext('div').table.find_all('div', {'class':'outcome-block'})
    s_timeframes = soup.find('p', text='Secondary outcome(s)').findNext('div').table.find_all('em', {'class':'custom-inline'})

    s_outcome_list = []
    for s, t in zip(s_outcomes, s_timeframes):
        outcome_dict = {}
        if not pat.match(s.text) and t.text != '[]':
            outcome_dict['outcome'] = s.text.strip().replace('\n','')
            outcome_dict['timeframe'] = t.text.strip().replace('\n','').replace('[','').replace(']','')
            outcome_list.append(outcome_dict)
        elif pat.match(s.text) and t.text != '[]':
            outcome_dict['outcome'] = None
            outcome_dict['timeframe'] = t.text.strip().replace('\n','').replace('[','').replace(']','')
            outcome_list.append(outcome_dict)
        elif not pat.match(s.text) and t.text == '[]': 
            outcome_dict['outcome'] = s.text.strip().replace('\n','')
            outcome_dict['timeframe'] = None
            outcome_list.append(outcome_dict)
        else:
            pass

    t_d['secondary_outcomes'] = s_outcome_list

    t_d['target_enrollment'] = normal_field(soup,'Target number/sample size')
    countries = normal_field(soup,'Countries of recruitment')
    if ',' in countries:
        t_d['recruitment_countries'] = countries.split(', ')
    else:
        t_d['recruitment_countries'] = normal_field(soup,'Countries of recruitment')
    t_d['anticipated_start_date'] = normal_field(soup,'Anticipated start date')
    t_d['anticipated_completion_date'] = normal_field(soup,'Anticipated end date')
    t_d['first_enrollment_date'] = normal_field(soup,'Date of first enrollment')
    t_d['study_completion_date'] = normal_field(soup,'Date of study completion')
    t_d['trial_status'] = normal_field(soup,'Recruitment status')
    t_d['funcing_source'] = normal_field(soup,'Funding source')
    t_d['regulatory_approvals'] = normal_field(soup,'Regulatory approvals')

    ethics_information = {}
    ethics_information['status'] = normal_field(soup,'Status')
    ethics_information['approval_date'] = normal_field(soup,'Date of Approval')
    ethics_information['approval_number'] = normal_field(soup,'Approval number')
    ethics_information['committee'] = soup.find('span', text='Name:').findNext('span').text.strip()
    ethics_information['address'] = soup.find('span', text='Institutional Address:').findNext('span').text.strip().replace('\r','').replace('\n',' ')
    ethics_information['phone'] = soup.find('span', text='Telephone:').findNext('span').text.strip()
    ethics_information['email'] = soup.find('span', text='Email:').findNext('span').text.strip()

    t_d['ethics_information'] = ethics_information
    t_d['scientific_contact'] = normal_field(soup,'Contact person for Scientific Queries/Principal Investigator').replace('\r','').replace('\n',' ')
    t_d['public_contact'] = normal_field(soup,'Contact Person for Public Queries').replace('\r','').replace('\n',' ')
    t_d['primary_sponsor'] = normal_field(soup,'Primary study sponsor/organization').replace('\r','').replace('\n',' ')
    t_d['secondary_sponsor'] = normal_field(soup,'Secondary study sponsor (If any)').replace('\r','').replace('\n',' ')

    t_d['ipd_sharing'] = normal_field(soup,'Do the investigators plan to share identified individual clinical trial participant-level data (IPD)?')
    t_d['ipd_sharing_plan'] = normal_field(soup, 'IPD sharing plan description')
    t_d['protocol_available']  = normal_field(soup, 'Study protocol available')
    t_d['protocol_version_date']  = normal_field(soup, 'Protocol version and date')
    t_d['protocol_url']  = soup.find('p', text='Protocol URL').findNext('div').text.strip()
    t_d['summary_results_available']  = normal_field(soup, 'Results summary available')
    t_d['results_posting_date']  = normal_field(soup, 'Date of posting results')
    t_d['final_completion_date'] = normal_field(soup, 'Date of study completion')
    t_d['final_enrollment']  = normal_field(soup, 'Final sample size')
    t_d['date_of_first_publication']  = normal_field(soup, 'Date of first publication')
    t_d['link_to_results'] = soup.find('p', text='Link to results').findNext('div').text.strip()
    t_d['results_summary']  = normal_field(soup, 'Brief summary of results')
    return t_d


# -

def table_check(soup):
    if soup.find('table', {'class':'table table-striped'}):
        return 1
    else:
        return 0


# +
trial_data = []

for i in tqdm(id_list):
    soup = get_url(base_trial_urls + i)
    trial_info = get_row(soup)
    pubs = get_url(base_trial_urls + i + '/publications')
    trial_info['pubs_in_tab'] = table_check(pubs)
    prog = get_url(base_trial_urls + i + '/progresses')
    trial_info['prog_in_tab'] = table_check(prog)
    trial_data.append(trial_info)
# -

headers = ['trial_id', 'trial_title', 'registration_date', 'last_updated_date', 'scientific_title', 'public_title', 
           'brief_title', 'study_disease_condition', 'scientific_acronym', 'public_acronym', 'universal_trial_number', 
           'other_trial_ids', 'research_question', 'study_type', 'allocation', 'masking', 'control', 'assignment', 'purpose', 
           'phase', 'planned_intervention', 'inclusion_criteria', 'exclusion_criteria', 'primary_outcomes', 'secondary_outcomes',
           'target_enrollment', 'recruitment_countries', 'anticipated_start_date', 'anticipated_completion_date', 
           'first_enrollment_date', 'study_completion_date', 'trial_status', 'funcing_source', 'regulatory_approvals',
           'ethics_information', 'scientific_contact', 'public_contact', 'primary_sponsor', 'secondary_sponsor',
           'ipd_sharing', 'ipd_sharing_plan', 'protocol_available', 'protocol_version_date', 'protocol_url',
           'summary_results_available', 'results_posting_date', 'final_completion_date', 'final_enrollment', 
           'date_of_first_publication', 'link_to_results', 'results_summary', 'pubs_in_tab', 'prog_in_tab']

# +
from datetime import date

with open('slctr_trials_{}.csv'.format(date.today()), 'w', newline='', encoding='utf-8') as slctr_csv:
    writer = csv.DictWriter(slctr_csv, fieldnames=headers)
    writer.writeheader()
    for td in trial_data:
        writer.writerow(td)
# -






