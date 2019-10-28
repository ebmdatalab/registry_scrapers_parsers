# -*- coding: utf-8 -*-
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


# +
def mult_tables(soup, sec_name, labels, secondary_labels=None):
    sect_list = []
    if not soup.find('h3', text=re.compile(sec_name)).findNext('div').findNext('div', {'class':'empty-section'}):
        for sub_s in soup.find('h3', text=re.compile(sec_name)).parent.find_all('div', {'class': 'subsection'}):
            sect_group = {}
            counter = 0
            for dd in sub_s.find_all('dd'):
                if dd.find('div', {'class': 'well contact-card'}):
                    sect_dict = {}
                    for l, t in zip(secondary_labels, dd.find_all('div', {'class': 'col-md-9 contact-value'})):
                        sect_dict[l] = t.text.strip()
                    sect_group[labels[counter]] = sect_dict
                    counter+=1
                else:
                    sect_group[labels[counter]] = dd.text.strip()
                    counter+=1
            sect_list.append(sect_group)
    else:
        sect_list = []
    return sect_list

def get_row(soup):
    t_d = {}
    t_d['trial_id'] = soup.find('span', text='IRCT registration number:').findNext('strong').text
    t_d['trial_name'] = soup.find('div', {'class':'page-header'}).text.strip()
    #dates in Y-M-D format with leading 0s for M and D
    t_d['registration_date'] = soup.find('span', text='Registration date:').findNext('strong').text[:10]
    t_d['registration_timing'] = soup.find('span', text='Registration timing:').findNext('strong').text
    t_d['last_updated_date'] = soup.find('span', text='Last update:').findNext('strong').text[:10]
    t_d['number_of_updates'] = soup.find('span', text='Update count:').findNext('strong').text
    if soup.find('dt', text=re.compile('Summary')):
        t_d['trial_summary'] = soup.find('dt', text=re.compile('Summary')).findNext('div').text.strip()
    else:
        t_d['trial_summary'] = None

    registrant_info = {}
    registrant_info['name'] = soup.find('dt', text=re.compile('Registrant information')).findNext('div').find('strong', text='Name').findNext('div').text.strip()
    registrant_info['organization'] = soup.find('dt', text=re.compile('Registrant information')).findNext('div').find('strong', text='Name of organization / entity').findNext('div').text.strip()
    registrant_info['country'] = soup.find('dt', text=re.compile('Registrant information')).findNext('div').find('strong', text='Country').findNext('div').text.strip()
    registrant_info['phone'] = soup.find('dt', text=re.compile('Registrant information')).findNext('div').find('strong', text='Phone').findNext('div').text.strip()
    registrant_info['email'] = soup.find('dt', text=re.compile('Registrant information')).findNext('div').find('strong', text='Email address').findNext('div').text.strip()
    t_d['registrant_info'] = registrant_info
    t_d['trial_status'] = soup.find('dt', text=re.compile('Recruitment status')).findNext('strong').text.strip()
    t_d['funding_source'] = soup.find('dt', text=re.compile('Funding source')).findNext('div').text.strip().replace('ِِ','')
    t_d['expected_start_date'] = soup.find('dt', text=re.compile('Expected recruitment start date')).findNext('dd').text.strip()[:10]
    t_d['expected_recruitment_end_date'] = soup.find('dt', text=re.compile('Expected recruitment end date')).findNext('dd').text.strip()[:10]
    t_d['actual_start_date'] = soup.find('dt', text=re.compile('Actual recruitment start date')).findNext('dd').text.strip()[:10]
    t_d['actual_recruitment_end_date'] = soup.find('dt', text=re.compile('Actual recruitment end date')).findNext('dd').text.strip()[:10]
    t_d['trial_completion_date'] = soup.find('dt', text=re.compile('Trial completion date')).findNext('dd').text.strip()[:10]
    t_d['scientific_title'] = soup.find('dt', text=re.compile('Scientific title')).findNext('dd').text.strip()
    t_d['public_title'] = soup.find('dt', text=re.compile('Public title')).findNext('dd').text.strip()
    t_d['trial_purpose'] = soup.find('dt', text=re.compile('Purpose')).findNext('dd').text.strip()
    t_d['inclusion_exclusion_criteria'] = soup.find('dt', text=re.compile('Inclusion/Exclusion criteria')).findNext('dd').text.strip()
    t_d['subject_age'] = soup.find('dt', text=re.compile('Age')).findNext('dd').text.strip()
    t_d['subject_gender'] = soup.find('dt', text=re.compile('Gender')).findNext('dd').text.strip()
    if soup.find('dt', text=re.compile('Phase')).findNext('dd').text.strip() == 'N/A':
        t_d['phase'] = 'N/A'
    else:
        t_d['phase'] = 'phase ' + soup.find('dt', text=re.compile('Phase')).findNext('dd').text.strip()
    t_d['masking'] =  soup.find('dt', text=re.compile('Groups that have been masked')).findNext('dd').text.strip()
    t_d['sample_size'] = soup.find('dt', text=re.compile('Sample size')).findNext('dd').findNext('strong').text.strip()
    t_d['randomization'] = soup.find('dt', text=re.compile("Randomization \(investigator's opinion\)")).findNext('dd').text.strip()
    t_d['randomization_description'] = soup.find('dt', text=re.compile("Randomization description")).findNext('dd').text.strip()
    t_d['blinding'] = soup.find('dt', text=re.compile("Blinding \(investigator's opinion\)")).findNext('dd').text.strip()
    t_d['blinding_description'] = soup.find('dt', text=re.compile("Blinding description")).findNext('dd').text.strip()
    t_d['placebo'] = soup.find('dt', text=re.compile("Placebo")).findNext('dd').text.strip()
    t_d['assignment'] = soup.find('dt', text=re.compile("Assignment")).findNext('dd').text.strip()
    t_d['other_design_features'] = soup.find('dt', text=re.compile("Other design features")).findNext('dd').text.strip()
    t_d['secondary_ids'] = mult_tables(soup, 'Secondary Ids', ['registry_name', 'secondary_id', 'registration_date'])
    t_d['ethics_information'] = mult_tables(soup, 'Ethics committees', ['ethics_committee', 'approval_date', 'reference_number'], secondary_labels=['committee_name', 'address', 'city', 'postal_code'])
    t_d['health_conditions'] = mult_tables(soup,'Health conditions studied', ['condition_description', 'icd_10_code', 'icd_10_description'])
    t_d['primary_outcomes'] = mult_tables(soup,'Primary outcomes', ['description', 'timepoint', 'measurement_method'])
    t_d['secondary_outcomes'] = mult_tables(soup,'Secondary outcomes', ['description', 'timepoint', 'measurement_method'])
    t_d['intervention_groups'] = mult_tables(soup,'Intervention groups', ['description', 'category'])
    t_d['recruitement_centers'] = mult_tables(soup,'Recruitment centers', ['center_info'], secondary_labels=['name', 'responsible_party', 'address', 'city'])
    t_d['sponsor_funding_sources'] = mult_tables(soup,'Sponsors / Funding sources', ['sponsor_contact', 'grant_name', 'grant_number', 'funding_same_as_sponsor', 
                                                    'funder_title', 'proportion_of_funding', 'public_of_private', 
                                                    'domestic_or_foreign', 'forgeign_source_category', 'country_of_origin', 'org_type'], 
                secondary_labels=['name', 'responsible_party', 'address', 'city'])

    general_inquiries = {}
    if soup.find('h3', text=re.compile('Person responsible for general inquiries')).findNext('div', {'class': 'well contact-card'}).text.strip() == '':
        t_d['general_contact'] = general_inquiries
    else:
        general_inquiries['organization'] = soup.find('h3', text=re.compile('Person responsible for general inquiries')).findNext('div').find('strong', text='Name of organization / entity').findNext('div').text.strip()
        general_inquiries['responsible_party'] = soup.find('h3', text=re.compile('Person responsible for general inquiries')).findNext('div').find('strong', text='Full name of responsible person').findNext('div').text.strip()
        general_inquiries['position'] = soup.find('h3', text=re.compile('Person responsible for general inquiries')).findNext('div').find('strong', text='Position').findNext('div').text.strip()
        general_inquiries['other_areas_of_work'] = soup.find('h3', text=re.compile('Person responsible for general inquiries')).findNext('div').find('strong', text='Other areas of specialty/work').findNext('div').text.strip()
        general_inquiries['address'] = soup.find('h3', text=re.compile('Person responsible for general inquiries')).findNext('div').find('strong', text='Street address').findNext('div').text.strip()
        general_inquiries['city'] = soup.find('h3', text=re.compile('Person responsible for general inquiries')).findNext('div').find('strong', text='City').findNext('div').text.strip()
        general_inquiries['postal_code'] = soup.find('h3', text=re.compile('Person responsible for general inquiries')).findNext('div').find('strong', text='Postal code').findNext('div').text.strip()
        general_inquiries['phone'] = soup.find('h3', text=re.compile('Person responsible for general inquiries')).findNext('div').find('strong', text='Phone').findNext('div').text.strip()
        if soup.find('h3', text=re.compile('Person responsible for general inquiries')).findNext('div').find('strong', text='Fax'):
            general_inquiries['fax'] = soup.find('h3', text=re.compile('Person responsible for general inquiries')).findNext('div').find('strong', text='Fax').findNext('div').text.strip()
        else:
            general_inquiries['fax'] = None
        general_inquiries['email'] = soup.find('h3', text=re.compile('Person responsible for general inquiries')).findNext('div').find('strong', text='Email').findNext('div').text.strip()
        if soup.find('h3', text=re.compile('Person responsible for general inquiries')).findNext('div').find('strong', text='Web page address'):
            general_inquiries['web_page'] = soup.find('h3', text=re.compile('Person responsible for general inquiries')).findNext('div').find('strong', text='Web page address').findNext('div').text.strip()
        else:
            general_inquiries['web_page'] = None
        t_d['general_contact'] = general_inquiries

    scientific_inquiries = {}
    if soup.find('h3', text=re.compile('Person responsible for scientific inquiries')).findNext('div', {'class': 'well contact-card'}).text.strip() == '':
        t_d['scientific_contact'] = scientific_inquiries
    else:    
        scientific_inquiries['organization'] = soup.find('h3', text=re.compile('Person responsible for scientific inquiries')).findNext('div').find('strong', text='Name of organization / entity').findNext('div').text.strip()
        scientific_inquiries['responsible_party'] = soup.find('h3', text=re.compile('Person responsible for scientific inquiries')).findNext('div').find('strong', text='Full name of responsible person').findNext('div').text.strip()
        scientific_inquiries['position'] = soup.find('h3', text=re.compile('Person responsible for scientific inquiries')).findNext('div').find('strong', text='Position').findNext('div').text.strip()
        scientific_inquiries['other_areas_of_work'] = soup.find('h3', text=re.compile('Person responsible for scientific inquiries')).findNext('div').find('strong', text='Other areas of specialty/work').findNext('div').text.strip()
        scientific_inquiries['address'] = soup.find('h3', text=re.compile('Person responsible for scientific inquiries')).findNext('div').find('strong', text='Street address').findNext('div').text.strip()
        scientific_inquiries['city'] = soup.find('h3', text=re.compile('Person responsible for scientific inquiries')).findNext('div').find('strong', text='City').findNext('div').text.strip()
        scientific_inquiries['postal_code'] = soup.find('h3', text=re.compile('Person responsible for scientific inquiries')).findNext('div').find('strong', text='Postal code').findNext('div').text.strip()
        scientific_inquiries['phone'] = soup.find('h3', text=re.compile('Person responsible for scientific inquiries')).findNext('div').find('strong', text='Phone').findNext('div').text.strip()
        if soup.find('h3', text=re.compile('Person responsible for scientific inquiries')).findNext('div').find('strong', text='Fax'):
            scientific_inquiries['fax'] = soup.find('h3', text=re.compile('Person responsible for scientific inquiries')).findNext('div').find('strong', text='Fax').findNext('div').text.strip()
        else:
            scientific_inquiries['fax'] = None
        scientific_inquiries['email'] = soup.find('h3', text=re.compile('Person responsible for scientific inquiries')).findNext('div').find('strong', text='Email').findNext('div').text.strip()
        if soup.find('h3', text=re.compile('Person responsible for scientific inquiries')).findNext('div').find('strong', text='Web page address'):
            scientific_inquiries['web_page'] = soup.find('h3', text=re.compile('Person responsible for scientific inquiries')).findNext('div').find('strong', text='Web page address').findNext('div').text.strip()
        else:
            scientific_inquiries['web_page'] = None
        t_d['scientific_contact'] = scientific_inquiries

    data_uploading = {}
    if soup.find('h3', text=re.compile('Person responsible for updating data')).findNext('div', {'class': 'well contact-card'}).text.strip() == '':
        t_d['data_update_responsible'] = data_uploading
    else:
        data_uploading['organization'] = soup.find('h3', text=re.compile('Person responsible for updating data')).findNext('div').find('strong', text='Name of organization / entity').findNext('div').text.strip()
        data_uploading['responsible_party'] = soup.find('h3', text=re.compile('Person responsible for updating data')).findNext('div').find('strong', text='Full name of responsible person').findNext('div').text.strip()
        data_uploading['position'] = soup.find('h3', text=re.compile('Person responsible for updating data')).findNext('div').find('strong', text='Position').findNext('div').text.strip()
        data_uploading['other_areas_of_work'] = soup.find('h3', text=re.compile('Person responsible for updating data')).findNext('div').find('strong', text='Other areas of specialty/work').findNext('div').text.strip()
        data_uploading['address'] = soup.find('h3', text=re.compile('Person responsible for updating data')).findNext('div').find('strong', text='Street address').findNext('div').text.strip()
        data_uploading['city'] = soup.find('h3', text=re.compile('Person responsible for updating data')).findNext('div').find('strong', text='City').findNext('div').text.strip()
        data_uploading['postal_code'] = soup.find('h3', text=re.compile('Person responsible for updating data')).findNext('div').find('strong', text='Postal code').findNext('div').text.strip()
        data_uploading['phone'] = soup.find('h3', text=re.compile('Person responsible for updating data')).findNext('div').find('strong', text='Phone').findNext('div').text.strip()
        if soup.find('h3', text=re.compile('Person responsible for updating data')).findNext('div').find('strong', text='Fax'):
            data_uploading['fax'] = soup.find('h3', text=re.compile('Person responsible for updating data')).findNext('div').find('strong', text='Fax').findNext('div').text.strip()
        else:
            data_uploading['fax'] = None
        data_uploading['email'] = soup.find('h3', text=re.compile('Person responsible for updating data')).findNext('div').find('strong', text='Email').findNext('div').text.strip()
        if soup.find('h3', text=re.compile('Person responsible for updating data')).findNext('div').find('strong', text='Web page address'):
            data_uploading['web_page'] = soup.find('h3', text=re.compile('Person responsible for updating data')).findNext('div').find('strong', text='Web page address').findNext('div').text.strip()
        else:
            data_uploading['web_page'] = None
        t_d['data_update_responsible'] = data_uploading

    sharing_plan = {}
    sharing_plan['ipd_sharing'] = soup.find('h3', text=re.compile('Sharing plan')).findNext('div').find('dt', text=re.compile('Deidentified Individual Participant Data Set \(IPD\)')).findNext('dd').text.strip()
    sharing_plan['study_protocol'] = soup.find('h3', text=re.compile('Sharing plan')).findNext('div').find('dt', text=re.compile('Study Protocol')).findNext('dd').text.strip()
    sharing_plan['statistical_analysis_plan'] = soup.find('h3', text=re.compile('Sharing plan')).findNext('div').find('dt', text=re.compile('Statistical Analysis Plan')).findNext('dd').text.strip()
    sharing_plan['informed_consent_form'] = soup.find('h3', text=re.compile('Sharing plan')).findNext('div').find('dt', text=re.compile('Informed Consent Form')).findNext('dd').text.strip()
    sharing_plan['clinical_study_report'] = soup.find('h3', text=re.compile('Sharing plan')).findNext('div').find('dt', text=re.compile('Clinical Study Report')).findNext('dd').text.strip()
    sharing_plan['analytic_code'] = soup.find('h3', text=re.compile('Sharing plan')).findNext('div').find('dt', text=re.compile('Analytic Code')).findNext('dd').text.strip()
    sharing_plan['data_dictionary'] = soup.find('h3', text=re.compile('Sharing plan')).findNext('div').find('dt', text=re.compile('Data Dictionary')).findNext('dd').text.strip()
    t_d['sharing_plan'] = sharing_plan
    return t_d


# -

headers = ['trial_id', 'trial_name', 'registration_date', 'registration_timing', 'last_updated_date', 'number_of_updates',
           'trial_summary', 'registrant_info', 'trial_status', 'funding_source', 'expected_start_date', 
           'expected_recruitment_end_date', 'actual_start_date', 'actual_recruitment_end_date', 'trial_completion_date', 
           'scientific_title', 'public_title', 'trial_purpose', 'inclusion_exclusion_criteria', 'subject_age', 'subject_gender', 'phase', 'masking', 'sample_size',
           'randomization', 'randomization_description', 'blinding', 'blinding_description', 'placebo', 'assignment', 
           'other_design_features', 'secondary_ids', 'ethics_information', 'health_conditions', 'primary_outcomes', 
           'secondary_outcomes', 'intervention_groups', 'recruitement_centers', 'sponsor_funding_sources', 'general_contact', 
           'scientific_contact', 'data_update_responsible', 'sharing_plan']

# +
#There are currently 22,217 registered trials in the IRCT as of 28 Oct 2019. The trials are numbered sequentially,
#But there is no good way to get the max trial number. It appears that the highest trials are around 40,000 so we will use
#50000 as a safe number. Will check to make sure this tracks

trial_ids = list(range(0,50000))
base_irct_url = 'https://www.irct.ir/trial/'
# -

start_time = time()
with open('irct_trials.csv', 'w', newline='', encoding='utf-8') as irct_csv:
    writer = csv.DictWriter(irct_csv, fieldnames=headers)
    writer.writeheader()
    request = 0
    for i in tqdm(trial_ids[0:500]):
        soup = get_url(base_irct_url + str(i))
        if soup.find('div', {'class':'message'}, text=re.compile('Not Found')):
            pass
        else:
            try:
                trial_info = get_row(soup)
                writer.writerow(trial_info)
            except Exception as e:
                import sys
                raise type(e)(str(e) + '\n' + 'Error trial: {}'.format(i)).with_traceback(sys.exc_info()[2])
end_time = time()
print('Scrape Finished in {} minutes'.format(round((end_time-start_time) / 60),0))

# +
#check this with smaller sample
