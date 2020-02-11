# registry_scrapers_parsers
Code to scrape/handle/extract data from various ICTRP Primary Registries.

## Notes:

-Many of these make use of Selenium and ChromeDriver (at the moment) at a discrete path, not as an environmental PATH variable. Make sure to modify to fit your file system and ChromeDriver (or other browser Driver) implementation

-The strategoy for each registry varies considerably based on how they make data available and how easy it is to interact with. For some it is simply a matter of downloading and parsing an XML file, for others it is much more involved. Outputs can be ndjson (usually in a .csv format though) or a standard CSV with data columns. For some we ony exact fields needed for our current use-case.

-Jupyter notebooks are used for prototyping and testing however the notebooks are shared alongside the paired Jupytext file as a script.

-Not all scrapers will work cross-platform at the moment. 

There are 18 ICTRP Primary Registries and Data Provicers

We already have code to scrape and/or handle data from:

ClinicalTrials.gov:
https://github.com/ebmdatalab/clinicaltrials-act-tracker

EUCTR Protocols:
https://github.com/ebmdatalab/euctr-tracker-code

Status of Additional Registries:

EUCTR Results Pages - Built and Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/EUCTR%20(EU)/Results%20Section%20Scrape

EUCTR Sponsor Country - Built and Test (Note: Have to run as script, not in notebook. This code is admittedly a bit of a mess but it works)
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/EUCTR%20(EU)/Sponsor%20Country%20Scrape

ANZCTR - Built and Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/ANZCTR%20(AusNZ)
Note: This gets XML from the website and parses it. This is a more flexible approach as you can export discrete searches, via URL, as needed and the XML is very complete. ANZCTR also has an easy crawling interface here if you are interested in that approach: http://www.anzctr.org.au/crawl.aspx

CRIS - Built and Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/CRiS%20(S.%20Korea)

Rebec - Built Tested (However to be improved):
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/ReBec%20(Brazil)

REPEC - Built and Partially Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/REPEC%20(Peru)

ChiCTR - Under Development but might be impossible to scrape cheaply and easily

ISRCTN - Not Necessary at present:
Can generate a CSV of most registry values for entire registry natively through website search by putting registration dates far in the future and the past.
Previous ISRCTN Scraper available here
https://github.com/opentrials/collectors/tree/master/collectors/isrctn

TCTR - Built Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/TCTR%20(Thailand)

NTR - Built and Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/NTR%20(Netherlands)

CTRI - Built and Partially Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/CTRI%20(India)

DRKS - Built and Tested
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/DRKS%20(Germany)

PACTR - Built and Partially Tested
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/PACTR%20(Africa)

JPRN - Built and Partially Tested
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/JPRN%20(Japan)

SLCTR - Built and Partially Tested
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/SLCTR%20(Sri%20Lanka)

IRCT - Built Tested (on Mac)
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/IRCT%20(Iran)

RPCEC - To Build

LBCTR - To Build




