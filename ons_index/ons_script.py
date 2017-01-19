import urllib2, json
from ons_output import OnsElasticsearchIndexer, OnsSimpleDocFormatter

SEARCH_URL = "https://www.ons.gov.uk/publications/data?sortBy=release_date" \
             "&query=&filter=bulletin&filter=article&filter=compendia&size=100&page="
ONS_URL = "https://www.ons.gov.uk/"

outputter = OnsElasticsearchIndexer()
formatter = OnsSimpleDocFormatter()

def get_search_page(page_no):
    url = SEARCH_URL + str(page_no)
    ons_request = urllib2.Request(url,
                              headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"})
    return json.loads(urllib2.urlopen(ons_request).read())

def get_search_page(page_no):
    url = SEARCH_URL + str(page_no)
    ons_request = urllib2.Request(url,
                              headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"})
    return json.loads(urllib2.urlopen(ons_request).read())

def get_ons_page(uri):
    url = ONS_URL + uri + "/data"
    ons_request = urllib2.Request(url,
                              headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"})
    return json.loads(urllib2.urlopen(ons_request).read())

def build_content(sections):
    content = ""
    for section in sections:
        content = content + section['title'] + '\n' + section['markdown'] + '\n'
    return content

# Set up the search
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

for page_no in range(0, len(results)):
    try:
        page = get_ons_page(results[page_no]['uri'])
        if 'sections' in page:
            results[page_no]['content'] = build_content(page['sections'])
        else:
            results[page_no]['content'] = ''

        print str(page_no) + ": Downloaded sections for " + page['uri']
    except:
        print("Could not parse ", page['uri'])

for doc in results:
    try:
        json = formatter.convert(doc)
        outputter.process(json)
    except:
        print("Error: Could not convert")



print("min: ", page_min, "max: ", page_max, "total results: ", len(results))
