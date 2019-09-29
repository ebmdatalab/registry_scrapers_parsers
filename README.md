# registry_scrapers_parsers
Code to scrape/handle/extract data from various ICTRP Primary Registries.

Notes:

-Many of these make use of Selenium and ChromeDriver at a discrete path, not as an environmental PATH variable. Make sure to modify to fit your file system and ChromeDriver (or other browser Driver) implementation

-The default is to get all trials from XML into a dictionary format for easier handling either via further python processing or SQL. The exact fields needed are likely to vary by use-case. Individual elements can be called either within python or exported as a CSV with 1 column of JSON strings, 1 row per trial, which can be used with other applications.

-Jupyter notebooks are used for prototyping and testing. The notebooks are shared alongside the paired Jupytext file as a script. 

-Each script will come with a function at the end that can be called to export a CSV.

There are 18 ICTRP Primary Registries and Data Provicers

We already have code to scrape and/or handle data from:

ClinicalTrials.gov:
https://github.com/ebmdatalab/clinicaltrials-act-tracker

EUCTR Protocols:
https://github.com/ebmdatalab/euctr-tracker-code

Status of Additional Registries:

EUCTR Results Pages - Built and Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/EUCTR%20(EU)/Results%20Section%20Scrape

EUCTR Sponsor Country - Built and Test (Note: Have to run as script, not in notebook)
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/EUCTR%20(EU)/Sponsor%20Country%20Scrape

ANZCTR - Built and Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/ANZCTR%20(AusNZ)
Note: This gets XML from the website and parses it. This is a more flexible approach as you can export discrete searches, via URL, as needed. ANZCTR also has an easy crawling interface here if you are interested in that approach: http://www.anzctr.org.au/crawl.aspx

CRIS - Built and Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/CRiS%20(S.%20Korea)

Rebec - Built Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/ReBec%20(Brazil)

REPEC - Built and Partially Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/REPEC%20(Peru)

ChiCTR - Under Development but might be impossible to scrape cheaply and easily

ISRCTN - Not Necessary at present:
Can generate a CSV of most registry values for entire registry natively through website search.
Previous ISRCTN Scraper available here
https://github.com/opentrials/collectors/tree/master/collectors/isrctn

TCTR - Built and Partially Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/TCTR%20(Thailand)

NTR - Built and Partially Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/NTR%20(Netherlands)

CTRI - Built and Partially Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/CTRI%20(India)

DRKS - Built and Partially Tested
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/DRKS%20(Germany)

PACTR - Built and Partially Tested
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/PACTR%20(Africa)

RPCEC - To Build

IRCT - To Build

JPRN - To Build

SLCTR - To Build

LBCTR - To Build




