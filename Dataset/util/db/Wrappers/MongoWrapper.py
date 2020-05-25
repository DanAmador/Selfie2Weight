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
    def get_unsanitized(get_first=False) -> RawEntry:
        resp = RawEntry.objects(has_been_sanitized=False).first()
        return resp

    @staticmethod
    def get_by(model: Document, query, only_first=True):
        return model.objects(__raw__=query).first() if only_first else model.objects(__raw__=query)

    @staticmethod
    def save_object(document: Document):
        try:
            u = {f"set__{key}": document.__getattribute__(key) for key in document._fields_ordered if
                 key != "id" and document.__getattribute__(key) is not None}
            type(document).objects(reddit_id=document.reddit_id).update_one(upsert=True, **u)
            return True
        except Exception as e:
            dataset_logger.error(e)
            return False
