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

import requests
from bs4 import BeautifulSoup
try:
    get_ipython
    from tqdm.notebook import tqdm
except NameError:
    from tqdm import tqdm


# +
def get_pages(pages, doc):
    new_sufs = []
    for page in pages:
        form_data = {
            "__EVENTTARGET": None,
            "ctl00$MainContent$ctrlSearch$hdnSearchType": "1",
            "ctl00$MainContent$ctrlSearch$txtBasicSearch": "PACTR",
        }
        if len(str(page)) == 1:
            page = str(page).zfill(2)
        et = "ctl00$MainContent$ctrlSearch$rptPager$ctl{}$lbPageNumber"
        form_data["__EVENTTARGET"] = et.format(page)
        for i in doc.find("form").find_all("input"):
            if i["id"].startswith("__"):
                form_data[i["id"]] = i["value"]
        rsp = session.post(url, form_data)       
        soup = BeautifulSoup(rsp.text, "html.parser")
        for l in soup.find_all('div', {'class':'col-md-6 col-sm-6 text-right resultHeader'}):
            new_sufs.append(l.find('a').get('href'))
    return new_sufs, soup

def next_pages(doc):
    # Extract form data for next set of pages
    form_data = {
        "__EVENTTARGET": "ctl00$MainContent$ctrlSearch$lbNextPage",
        "ctl00$MainContent$ctrlSearch$hdnSearchType": "1",
        "ctl00$MainContent$ctrlSearch$txtBasicSearch": "PACTR",
    }
    for i in doc.find("form").find_all("input"):
        if i["id"].startswith("__"):
            form_data[i["id"]] = i["value"]

    # Get next set of pages
    rsp = session.post(url, form_data)
    doc = BeautifulSoup(rsp.text, "html.parser")
    return doc

def first_page(doc):
    suffs = []
    # Extract form data
    form_data = {
        "__EVENTTARGET": "ctl00$MainContent$ctrlSearch$rptPager$ctl00$lbPageNumber",
        "ctl00$MainContent$ctrlSearch$hdnSearchType": "1",
        "ctl00$MainContent$ctrlSearch$txtBasicSearch": "PACTR",
    }
    for i in doc.find("form").find_all("input"):
        if i["id"].startswith("__"):
            form_data[i["id"]] = i["value"]
    # Get page
    rsp = session.post(url, form_data)
    doc = BeautifulSoup(rsp.text, "html.parser")

    for l in doc.find_all('div', {'class':'col-md-6 col-sm-6 text-right resultHeader'}):
        suffs.append(l.find('a').get('href'))
    return suffs


# -

#setup
session = requests.Session()
url_suf = []
# Get homepage
url = "https://pactr.samrc.ac.za/Search.aspx"
rsp = session.get(url)

# Extract form data
doc = BeautifulSoup(rsp.text, "html.parser")
form_data = {
    "__EVENTTARGET": "ctl00$MainContent$ctrlSearch$lbBasicSearch",
    "ctl00$MainContent$ctrlSearch$hdnSearchType": "1",
    "ctl00$MainContent$ctrlSearch$txtBasicSearch": "PACTR",
}
for i in doc.find("form").find_all("input"):
    if i["id"].startswith("__"):
        form_data[i["id"]] = i["value"]

# Do search (this returns page 1)
rsp = session.post(url, form_data)
soup = BeautifulSoup(rsp.text, "html.parser")

for l in soup.find_all('div', {'class':'col-md-6 col-sm-6 text-right resultHeader'}):
    url_suf.append(l.find('a').get('href'))

# +
iterations = list(range(1,13))
pages = list(range(1,20))

counter = 1
for i in tqdm(iterations):
    if counter < len(iterations):
        #this searches a set of pages
        output = get_pages(pages, soup)

        #take the list output and add it to our overall one
        url_suf = url_suf + output[0]

        #the new doc to get the next set of pages
        doc = output[1]

        soup = next_pages(doc)

        url_suf = url_suf + first_page(soup)
        counter +=1
    else:
        #This range will be from 1 to 1 + the number of pages on the last set of pages on PACTR
        pages = list(range(1,2))
        output = get_pages(pages, soup)
        url_suf = url_suf + output[0]
# -

print('All URLs: {}'.format(len(url_suf)))

final_urls = list(set(url_suf))

print('Unique URLs: {}'.format(len(final_urls)))

# +
from requests import get
from bs4 import BeautifulSoup
import re
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
trial_description_labels = ['public_title', 'scientific_title', 'background', 'study_type', 'acronym', 'primary_conditions', 
                     'secondary_conditions', 'purpose', 'anticipated_start_date', 'actual_start_date', 
                     'anticipated_completion_date', 'actual_completion_date', 'anticiapted_enrollment', 'actual_enrollment', 
                     'recruitment_status', 'publication_url']

design_labels = ['intervention_assignment', 'allocation_process', 'randomisation_generation', 'allocation_concealment', 
                 'masking', 'masking_blinding_used']

int_labels = ['intervention_type', 'intervention_name', 'dose', 'duration', 'intervention_description', 'group_size',
                      'nature_of_control']

elig_labels = ['inclusion_criteria', 'exclusion_criteria', 'age_category', 'min_age', 'max_age', 'gender']

ethics_labels = ['recieved_ethics', 'date_to_be_submitted_approval', 'date_of_approval', 'ethics_committee', 
                 'committee_address']

ethics_address = ['address', 'city', 'postal_code', 'country']

outcome_labels = ['outcome_type', 'outcome', 'measurement_timepoints']

recruit_labels = ['centre_name', 'address', 'city', 'postal_code', 'country']

funding_labels = ['name_of_funder', 'address', 'city', 'postal_code' 'country']

spon_labels = ['sponsor_type', 'sponsor_name', 'address', 'city', 'postal_code', 'country', 'nature_of_sponsor']

collab_labels = ['name', 'address', 'city', 'postal_code', 'country']

contact_labels_1 = ['role', 'name', 'email', 'phone', 'address']

contact_labels_2 = ['city', 'postal_code', 'country', 'position_affiliation']

results_labels = ['share_ipd', 'description', 'additiona_documents', 'sharing_time_frame', 'key_access_criteria', 'url',
                 'results_available', 'results_summary', 'results_posting_date', 'first_journal_pub_date', 'results_url',
                 'baseline_characteristics', 'participant_flow', 'adverse_events', 'outcome_measures_description', 'protocol_link']

changes_labels = ['section', 'field_name', 'date', 'reason', 'old_value', 'updated_value']

def straight_tables(table_name, label_list):
    table = soup.find(text=re.compile(table_name)).parent.parent.parent.find_all('tr')
    tab_list = []
    for t in table[2:]:
        tds = t.find_all('td')
        tab_dict = {}
        for td, label in zip(tds, label_list):
            tab_dict[label] = td.text.strip()
        tab_list.append(tab_dict)
    return tab_list


# -

def get_trial_info(soup):    
    t_d = {}
    if soup.find(text=re.compile(r'PACTR\d{15}')):
        t_d['trial_id'] = soup.find(text=re.compile(r'PACTR\d{15}'))
        t_d['date_registered'] = soup.find(text=re.compile(r'Date registered')).parent.findNext('td').text.strip()
        t_d['registration_status'] = soup.find(text=re.compile(r'Trial Status')).parent.findNext('td').text.strip()

        trial_description = soup.find(text="TRIAL DESCRIPTION").parent.parent
        tr = trial_description.findNext('tr')
        for t_desc in trial_description_labels:
            t_d[t_desc] = tr.find('td', {'class':"info"}).text.strip()
            tr = tr.findNext('tr')

        s_i = soup.find(text=re.compile(r'Secondary Ids')).parent.parent.parent.parent
        all_ids = s_i.find_all('td', {'class': 'info'})
        secondary_ids = []
        idx = 0
        for n in list(range(0,(int(len(all_ids)/2)))):
            id_dict = {}
            id_dict['type'] = all_ids[idx].text.strip()
            id_dict['id_number'] = all_ids[idx+1].text.strip()
            if id_dict['type'] == '' and id_dict['id_number'] == '':
                pass
            elif id_dict:
                secondary_ids.append(id_dict)
            else:
                pass
            idx += 2
        t_d['secondary_ids'] = secondary_ids

        t_d['study_design'] = straight_tables('STUDY DESIGN', design_labels)

        t_d['interventions'] = straight_tables('INTERVENTIONS', int_labels)

        t_d['eligibility_criteria'] = straight_tables('ELIGIBILITY CRITERIA', elig_labels)

        ethics = soup.find(text=re.compile(r'ETHICS APPROVAL')).parent.parent.parent.find_all('tr')
        len_eth = len(ethics)
        eth_data_lines = list(range(2,len_eth, 6))
        address_lines = list(range(6, len_eth, 6))
        ethics_list = []
        for line, add_line in zip(eth_data_lines, address_lines):
            td = ethics[line].find_all('td')
            eth_dict={}
            for t, l in zip(td, ethics_labels[:-1]):
                eth_dict[l] = t.text.strip()
            add = ethics[add_line].find_all('td')
            add_dict={}
            for tag, lab in zip(add, ethics_address):
                add_dict[lab] = tag.text.strip()
            eth_dict[ethics_labels[-1]] = add_dict
            ethics_list.append(eth_dict)
        t_d['ethics_approval'] = ethics_list

        t_d['outcomes'] = straight_tables('OUTCOMES', outcome_labels)

        t_d['recruitment_centres'] = straight_tables('RECRUITMENT CENTRES', recruit_labels)

        t_d['funding_sources'] = straight_tables('FUNDING SOURCES', funding_labels)

        t_d['sponsors'] = straight_tables('SPONSORS', spon_labels)

        t_d['collaborators'] = straight_tables('COLLABORATORS', collab_labels)

        contact = soup.find(text=re.compile(r'CONTACT PEOPLE')).parent.parent.parent.find_all('tr')
        cont_lines_1 = list(range(2,len(contact),4))
        cont_lines_2 =list(range(4,len(contact),4))
        contact_list = []
        for line_1, line_2 in zip(cont_lines_1, cont_lines_2):
            tds_1 = contact[line_1].find_all('td')
            contact_dict = {}
            for t_1, lab_1 in zip(tds_1, contact_labels_1):
                contact_dict[lab_1] = t_1.text.strip()
            tds_2 = contact[line_2].find_all('td')
            for t_2, lab_2 in zip(tds_2, contact_labels_2):
                contact_dict[lab_2] = t_2.text.strip()
            contact_list.append(contact_dict)
        t_d['contact_people'] = contact_list

        reporting = soup.find(text=re.compile(r'REPORTING')).parent.parent.parent.find_all('tr')
        reporting_lines = list(range(2,9,2))
        reporting_data = []
        for n in reporting_lines:
            reporting_data = reporting_data + reporting[n].find_all('td')
        results_dict = {}
        for d, r in zip(reporting_data, results_labels):
            results_dict[r] = d.text.strip()
        t_d['reporting'] = results_dict

        t_d['trial_history'] = straight_tables('Changes to trial information', changes_labels)

        return t_d


# +
base_url = 'https://pactr.samrc.ac.za/'

trial_list = []
for page in tqdm(final_urls):
    url = base_url + page
    soup = get_url(url)
    trial_check = soup.find(text=re.compile(r'Trial no.:'))
    if trial_check:
        id_check = trial_check.parent.find_next_sibling('td').find(text=re.compile(r'PACTR\d{15}'))
        if id_check:
            trial_info = get_trial_info(soup)
            trial_list.append(trial_info)
# -

print('Scraped Trials: {}'.format(len(trial_list)))

import ndjson
from datetime import date
with open('pactr_json_{}.ndjson'.format(date.today()),'w') as r:
    ndjson.dump(trial_list, r)


