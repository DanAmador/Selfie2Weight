import sqlite3
from contextlib import contextmanager
from pathlib import Path

import ElasticSearch as ElasticSearch
from sqlalchemy.orm import sessionmaker, scoped_session

from Dataset.util.dataset_logger import dataset_logger as logger
from sqlalchemy import create_engine, and_

from Dataset.util.db.base_class import Base
from Dataset.util.db.model import RawEntry
from sqlalchemy.sql.expression import func, select

p = Path().cwd().parent / "Scrapper" / 'dump'

from abc import ABC, abstractmethod


class AbstractDBWrapper(ABC):

    @contextmanager
    def session_scope(self):
        raise NotImplementedError

    @staticmethod
    def get_unsanitized(session, get_first=False):
        raise NotImplementedError

    @staticmethod
    def get_by(model, key, val, session, only_first=True):
        raise NotImplementedError

    @staticmethod
    def save_object(model, session):
        raise NotImplementedError
