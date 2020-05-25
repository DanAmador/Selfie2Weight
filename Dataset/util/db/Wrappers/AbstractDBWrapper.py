from contextlib import contextmanager
from pathlib import Path

p = Path().cwd().parent / "Scrapper" / 'dump'

from abc import ABC


class AbstractDBWrapper(ABC):

    @contextmanager
    def session_scope(self):
        raise NotImplementedError

    @staticmethod
    def get_unsanitized(get_first=False):
        raise NotImplementedError

    @staticmethod
    def get_by(model, query, only_first=True):
        raise NotImplementedError

    @staticmethod
    def save_object(model):
        raise NotImplementedError
