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

import requests
rsp = requests.post(
    "https://api.trialregister.nl/trials/public.trials/_msearch?",
    headers={"Content-Type": "application/x-ndjson", "Accept": "application/json"},
    data='{"preference":"results"}\n{"query":{"match_all":{}},"size":10000,"_source":{"includes":["*"],"excludes":[]},"sort":[{"id":{"order":"desc"}}]}\n',
)
results = rsp.json()
hits = results["responses"][0]["hits"]["hits"]
records = [hit["_source"] for hit in hits]

all_keys = set().union(*(record.keys() for record in records))

# +
labels = list(all_keys)

from datetime import date
import csv

def ntr_csv():
    with open('ntr - ' + str(date.today()) + '.csv','w', newline = '', encoding='utf-8') as ntr_csv:
        writer=csv.DictWriter(ntr_csv,fieldnames=labels)
        writer.writeheader()
        writer.writerows(records)


# -

ntr_csv()



