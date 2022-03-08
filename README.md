# registry_scrapers_parsers
Code to scrape/handle/extract data from various ICTRP Primary Registries.

## Notes:

* Some these make use of Selenium and ChromeDriver (at the moment) at a discrete path, not as an environmental PATH variable. Make sure to modify to fit your file system and ChromeDriver (or other browser Driver) implementation

* The strategy for each registry varies considerably based on how they make data available and how easy it is to interact with. For some it is simply a matter of downloading and parsing a single XML file, for others it is much more involved. Outputs can be ndjson (somtimes in a .csv format though) or a standard CSV with data columns, or some weird mix. For some we ony extract fields needed for our current use-case.

* Jupyter notebooks are used for prototyping, development, and testing however the notebooks are shared alongside the paired Jupytext file.

* Not all scrapers will work cross-platform at the moment. See notes.

## Progress by registry

There are 18 ICTRP Primary Registries and Data Provicers

We already have code to scrape and/or handle data from:

ClinicalTrials.gov:
https://github.com/ebmdatalab/clinicaltrials-act-tracker  
**Strategy:** Downloads and parses the XML archive of the full registry that is updated daily

EUCTR Protocols:
https://github.com/ebmdatalab/euctr-tracker-code  
**Strategy:** A manual scraping of html built in Scrapy

Status of Additional Registries:

EUCTR Results Pages - Built and Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/EUCTR%20(EU)/Results%20Section%20Scrape  
**Strategy:** Manual scraping of html. 
*Note there is now both a standard and mutiprocessing version of this scraper available. The multiprocessing version is only tested on Mac.*

EUCTR Sponsor Country - Built and Tested on Mac only: 
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/EUCTR%20(EU)/Sponsor%20Country%20Scrape  
**Strategy:** Manual scraping of html now tidier! 

ANZCTR - Built and Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/ANZCTR%20(AusNZ)  
**Strategy:** This gets XML from the website and parses it. This is a more flexible approach as you can export discrete searches, via URL, as needed and the XML is very complete. ANZCTR also has an easy crawling interface here if you are interested in that approach: http://www.anzctr.org.au/crawl.aspx

CRIS - Built and Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/CRiS%20(S.%20Korea)  
**Strategy:** We have scripts to automatically download and parse the XML, however this doesn't contain the information on results that we need so a manual html scraper was built to grab only the information we need for now.

Rebec - Built and Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/ReBec%20(Brazil)  
**Strategy:** Use Selenium to download all the XMLs and then parse them  
*Note: This is a very clumsy implementation through Selenium. We have a strategy for improving it and will update soon*

REPEC - Built and Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/REPEC%20(Peru)
**Strategy:** Get XML and parse

ChiCTR - Under Development

ISRCTN - Not Necessary at present  
*Note: Can generate a CSV of most registry values for entire registry natively through website search by putting registration dates far in the future and the past. Previous ISRCTN Scraper available here: https://github.com/opentrials/collectors/tree/master/collectors/isrctn*

TCTR - Code is legacy. No scraper implemented yet for new version of the TCTR (https://www.thaiclinicaltrials.org/):
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/TCTR%20(Thailand)  
**Strategy:** Get the full XML of the registry and parse

NTR - Built and Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/NTR%20(Netherlands)  
**Strategy:** Interact with the hidden API to get the full database behind the registry

CTRI - Built and Tested:
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/CTRI%20(India)  
**Strategy:** Brute force visit all the possible URLs and scrape the html. Currently the scrape of all possible data does not work. We have a lighter weight scraping function available that only grabs what we need for our projects at present. A lighter footprint version of this scraper is potentially in the works.

DRKS - Built and Tested
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/DRKS%20(Germany)  
**Strategy:** Briefly uses Selenium to grab some information to inform the rest of the scrape which visits each trial page and gets the html

PACTR - Built and Tested
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/PACTR%20(Africa)
**Strategy:** We get all the trial suffixes that point to detailed trial information and then cycle through them for the full scrape. 

JPRN - Built and Partially Tested
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/JPRN%20(Japan)
**Strategy:** The UMIN database has a full CSV of all trials and that is the vast majority of trails on the JPRN so not developing this further at the moment. 

SLCTR - Built and Tested
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/SLCTR%20(Sri%20Lanka)  
**Strategy:** Straightforward grab of record ids then scrape of all trial info from html

IRCT - Built and Tested (SEE NOTE)
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/IRCT%20(Iran)  
**Strategy:** Get all the trial url suffixes then visit the trial XML pages and extract  
*Note: There is a regular version of this scraper and one which uses some multi-processing to speed things up. The multi-processing version is a little unfriendly and only works on Mac*

RPCEC - Built and Tested
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/RPCEC%20(Cuba)
**Strategy:** Get all the trial url suffixes then visit the trial pages and extract (along with the spanish language publications field)

LBCTR - Built and Tested
https://github.com/ebmdatalab/registry_scrapers_parsers/tree/master/LBCTR%20(Lebanon)
**Strategy:** Get all the trial url suffixes then visit the trial pages and extract trial info




