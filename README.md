# registry_scrapers_parsers
Code to scrape/handle/extract data from various ICTRP Primary Registries.

Notes:
-Many of these make use of Selenium and ChromeDriver at a discrete path, not as an environmental PATH variable. Make sure to modify to fit your file system and ChromeDriver (or other Driver) implementation
-The default is to get all trials from XML into JSON format for easier handling, especially with arrays. The exact fields needed are likely to vary by use-case. Individual elements can be called either within python or exported as a CSV with 1 column of JSON strings, 1 row per trial, which can be used with other applications.

There are 17 ICTRP Primary Registries and Data Provicers

We already have code to scrape and handle data from:

ClinicalTrials.gov:
https://github.com/ebmdatalab/clinicaltrials-act-tracker

EUCTR Protocols:
https://github.com/ebmdatalab/euctr-tracker-code

Status of Additional Registries:

EUCTR Results Pages - Built and Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/EUCTR/Results%20Section%20Scrape

ANZCTR - Built and Partially Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/ANZCTR%20(AusNZ)

CRIS - Built and Partially Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/CRiS%20(S.%20Korea)

Rebec - Built and Partially Tested:
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

CTRI - To Build

RPCEC - To Build

DRKS - To Build

IRCT - To Build

JPRN - To Build

PACTR - To Build

SLCTR - To Build

NTR - To Build


