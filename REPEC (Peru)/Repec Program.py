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

# # REPEC (Peru) Registry Scraper/Parser

# +
import xmltodict
import json
import os
from bs4 import BeautifulSoup
from requests import get
import html.parser
import re
from pathlib import Path
import platform

platform = platform.platform()
cwd = os.getcwd()
download_path = os.path.join(cwd,'REPEC Downloads')
#adjust this to fit your specific file structure 
parent = str(Path(cwd).parents[0])
# -

generate = get('https://www.ins.gob.pe/ensayosclinicos/rpec/GenerarXMLALL.asp?fbusqueda=&especialidad=%&estado=&anio=%&val=')
html_generate = generate.content
generate_page = BeautifulSoup(html_generate, "html.parser")

results_str = generate_page.find('body').text

print(results_str)

total_trials = int((re.findall(r"[0-9]{4}", results_str))[0])
print(total_trials)

url_end = generate_page.find('a').get('href')

response = get('https://www.ins.gob.pe/ensayosclinicos/rpec/' + url_end)
raw = response.text

repec_trials = []
trials = xmltodict.parse(raw, encoding = 'utf-8')

for trial in trials['trials']['trial']:
    rebec_trials.append(json.dumps(trial))

# +
#getting rid of leftover html entities

fixed_repec = []
for trial in rebec_trials:
    no_html = html.unescape(trial)
    fixed_rebec.append(no_html)
# -

print(json.loads(fixed_repec[0])['main']['primary_sponsor'])

if total_trials == len(fixed_repec):
    print("Success!: {} trials".format(total_trials))
else:
    print("Error! Rebec Trials {}, Scraped Trials {}".format(total_trials, len(fixed_repec)))

# +
from datetime import date
import csv

def repec_csv():
    with open('repec - '+ str(date.today()) + '.csv','w', newline = '')as repec_csv:
        writer=csv.writer(repec_csv)
        for json in fixed_rebec:
            writer.writerow([json])
# -


