import sqlite3
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy.orm import sessionmaker, scoped_session

from util.dataset_logger import dataset_logger as logger
from sqlalchemy import create_engine, and_

from util.db.Wrappers.AbstractDBWrapper import AbstractDBWrapper
from util.db.base_class import Base
from util.db.model import RawEntry
from sqlalchemy.sql.expression import func, select

p = Path().cwd().parent / "Scrapper" / 'dump'


class SQLWrapper(AbstractDBWrapper):
    def __init__(self, db_path=p) -> None:
        db_path = db_path / "dump.sqlite"
        if not db_path.is_file():
            Path(db_path).touch()

        engine = create_engine(f"sqlite:///{db_path}")
        self.SessionClass = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
        Base.metadata.create_all(bind=engine)

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.SessionClass()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def get_unsanitized(session, get_first=False):
        query = session.query(RawEntry).filter(
            and_(RawEntry.has_been_sanitized == False, RawEntry.local_path.isnot(None))).order_by(func.random())
        if get_first:
            return query.first()
        return query.all()

    @staticmethod
    def get_by(model, key, val, session, only_first=True):
        q = session.query(model).filter_by(**{key: val})
        return q.first() if only_first else q.all()

    @staticmethod
    def save_object(model, session):
        try:
            model.save(session)
            return True
        except Exception as e:
            logger.error(e)

        return False
