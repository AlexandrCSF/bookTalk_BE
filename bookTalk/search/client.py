from elasticsearch import Elasticsearch, Transport


class ElasticClient:
    def __init__(self):
        self.url = "localhost:9200"
        self.client = Elasticsearch(hosts=self.url, transport_class=Transport)
        self.index = "booktalk"

    def search(self, query):
        request = {
            "query": {
                "match": {
                    "name": query
                }
            }
        }

        response = self.client.search(index=self.client.index, body=request)
        return [val['_source'] for val in response]

    def bulk(self, dict_to_send):
        self.client.bulk(index=self.client.index, body=dict_to_send)

    def indices(self):
        return self.client.indices