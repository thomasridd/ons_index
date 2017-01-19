import urllib2, json
from ons_output import OnsElasticsearchIndexer, OnsSimpleDocFormatter, OnsCompendiumFormatter

ONS_URL = "https://www.ons.gov.uk/"
SEARCH_URL = "publications/data?sortBy=release_date" \
             "&query=&filter=bulletin&filter=article&size=100&page="
COMPENDIUM_SEARCH_URL = "publications/data?sortBy=release_date&query=&filter=compendia&size=100&page="


# Set objects for required output format and method
outputter = OnsElasticsearchIndexer()
formatter = OnsSimpleDocFormatter()
compendium_formatter = OnsCompendiumFormatter()

def get_ons_page(uri):
    url = ONS_URL + uri + "/data"
    ons_request = urllib2.Request(url,
                              headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"})
    return json.loads(urllib2.urlopen(ons_request).read())

def get_search_page(page_no):
    url = ONS_URL + SEARCH_URL + str(page_no)
    ons_request = urllib2.Request(url,
                              headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"})
    return json.loads(urllib2.urlopen(ons_request).read())

def get_compendium_search_page(page_no):
    url = ONS_URL + COMPENDIUM_SEARCH_URL + str(page_no)
    ons_request = urllib2.Request(url,
                              headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"})
    return json.loads(urllib2.urlopen(ons_request).read())


# Find results for bulletins and articles
search = get_search_page(1)
page_min = 1
page_max = search['result']['paginator']['end']
results = []

for page_no in range(page_min, page_max + 1):
    search = get_search_page(page_no)
    try:
        results.extend(search['result']['results'])
    except:
        print("Search results failed on page ", page_no)


# Populate with content
for page_no in range(0, len(results)):
    try:
        page = get_ons_page(results[page_no]['uri'])
        if 'sections' in page:
            results[page_no]['sections'] = page['sections']

        print str(page_no) + ": Downloaded sections for " + page['uri']
    except:
        print("Could not parse ", page['uri'])

# Output
for doc in results:
    try:
        json_doc = formatter.convert(doc)
        outputter.process(json_doc)
    except:
        print("Error: Could not convert")


# Get compendium results
results = []
search = get_compendium_search_page(1)
page_min = 1
if 'paginator' in search['result']:
    page_max = search['result']['paginator']['end']
else:
    page_max = 1

for page_no in range(page_min, page_max + 1):
    search_results = search['result']['results']
    for search_result in search_results:
        try:
            compendium = get_ons_page(search_result['uri'])
            for chapter in compendium['chapters']:
                try:
                    results.append(get_ons_page(chapter['uri']))
                except:
                    print "Could not process chapter at uri " + chapter['uri']
        except:
            print "Could not process compendium at uri " + search_result['uri']

# Output for compendia
for doc in results:
    try:
        json_doc = compendium_formatter.convert(doc)
        outputter.process(json_doc)
    except:
        print("Error: Could not convert")



print("min: ", page_min, "max: ", page_max, "total results: ", len(results))
