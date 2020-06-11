from contextlib import contextmanager

from mongoengine import *

from util.dataset_logger import dataset_logger
from util.db.Wrappers.AbstractDBWrapper import AbstractDBWrapper


class MongoWrapper(AbstractDBWrapper):

    @staticmethod
    @contextmanager
    def session_scope(**kwargs):
        try:
            # AYY LMAO SECURITY
            s = connect("selfies")
            yield s
        except Exception  as e:
            print(e)
            raise e
        #finally:
            #disconnect()

    @staticmethod
    def get_by(model: Document, query, **kwargs):
        pipeline = [
            {
                "$match": query
            },
            {
                "$sample": {"size": 1}
            }

        ]
        docs = list(model.objects.aggregate(*pipeline))

        return docs[0] if len(docs) > 0 else {}

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
