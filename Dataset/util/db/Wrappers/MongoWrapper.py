from contextlib import contextmanager

from Dataset.util.db.SelfieMetadataIndex import SelfieMetadataIndex
from Dataset.util.db.Wrappers.AbstractDBWrapper import AbstractDBWrapper
from elasticsearch import Elasticsearch


class ElasticWrapper(AbstractDBWrapper):
    @contextmanager
    def session_scope(self):
        try:
            yield Elasticsearch(['localhost:9200'])
        except Exception  as e:
            print(e)

    def __init__(self):
        es = Elasticsearch(['localhost:9200'])
        self.index_name = "selfies"
        SelfieMetadataIndex.create_index(es, self.index_name)

    @staticmethod
    def get_unsanitized(session, get_first=False):
        query_body = {
            "query": {
                "bool": {
                    "must":
                        [
                            {
                                "term": {
                                    "doc.has_been_sanitized": True
                                }
                            }
                        ]

                }
            }
        }

        matches = session.search(body=query_body)

        return matches["hits"][0] if len(matches) > 0 and get_first else matches["hits"]

    @staticmethod
    def get_by(model, key, val, session, only_first=True):
        query_body = {
            "query": {
                "match": {
                    key: val
                }
            }
        }
        matches = session.search(body=query_body)

        return matches["hits"][0] if len(matches) > 0 and only_first else matches["hits"]

    @staticmethod
    def save_object(document, session):
        session.update(index="selfies", body={'doc': document, 'doc_as_upsert': True})
