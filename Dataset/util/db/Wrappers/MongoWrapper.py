from contextlib import contextmanager

from util.db.Wrappers.AbstractDBWrapper import AbstractDBWrapper
from mongoengine import *

from util.db.model import SanitizedEntry


class MongoWrapper(AbstractDBWrapper):
    @staticmethod
    @contextmanager
    def session_scope():
        try:
            yield connect(alias="session_scope")
        except Exception  as e:
            print(e)
        finally:
            disconnect(alias="session_scope")

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
    def save_object(document: SanitizedEntry, session):
        #TODO queries
        #Location.objects(reddit_id=document.reddit_id).update_one(set__point=point, upsert=True)

        session.update(index="selfies", body={'doc': document, 'doc_as_upsert': True})
