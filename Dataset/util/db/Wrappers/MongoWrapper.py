from contextlib import contextmanager

from util.dataset_logger import dataset_logger
from util.db.Wrappers.AbstractDBWrapper import AbstractDBWrapper
from mongoengine import *

from util.db.model import SanitizedEntry, RawEntry


class MongoWrapper(AbstractDBWrapper):

    @staticmethod
    @contextmanager
    def session_scope(**kwargs):
        try:
            # AYY LMAO SECURITY
            s = connect("selfies", username="root", password="rootpassword",
                        authentication_source='admin', alias="default")
            yield s
        except Exception  as e:
            print(e)
            raise e
        finally:
            disconnect(alias="default")

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
    def save_object(document: Document):
        try:
            u = {f"set__{key}": document.__getattribute__(key) for key in document._fields_ordered if key != "id" and document.__getattribute__(key) is not None}
            type(document).objects(reddit_id=document.reddit_id).update_one(upsert=True, **u)
            return True
        except Exception as e:
            dataset_logger.error(e)
            return False
