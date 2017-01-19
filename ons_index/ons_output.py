from elasticsearch import Elasticsearch

class OnsElasticsearchIndexer():
    es = Elasticsearch()

    def __init__(self):
        self.es.indices.delete(index='ons-index', ignore=[400, 404])
        self.es.indices.create(index='ons-index', ignore=400)

    def process(self, result):
        try:
            self.es.create(index='ons-index', doc_type='document', id=result['uri'], body=result)
        except:
            print("Could not process: ", result['uri'])


class OnsSimpleDocFormatter():
    def convert(self, doc):
        try:
            result = {}
            result['uri'] = doc['uri']
            description = doc['description']

            result['title'] = description['title']
            if 'summary' in description:
                result['summary'] = description['summary']
            elif '_abstract' in description:
                result['summary'] = description['_abstract']

            result['releaseDate'] = description['releaseDate']

            if 'edition' in description:
                result['edition'] = description['edition']
            else:
                result['edition'] = 'n/a'

            if 'metaDescription' in description:
                result['metaDescription'] = description['metaDescription']
            else:
                result['metaDescription'] = ''

            if 'content' in doc:
                result['content'] = doc['content']

            return result
        except:
            return {"error", "Could not convert document"}

