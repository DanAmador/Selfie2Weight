import sqlite3
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy.orm import sessionmaker, scoped_session

from Dataset.util.dataset_logger import dataset_logger as logger
from sqlalchemy import create_engine

from Dataset.util.db.base_class import Base
from Dataset.util.db.model import RawEntry

p = Path().cwd().parent / "Scrapper" / 'dump'


class DBWrapper:
    def __init__(self, db_path=p) -> None:
        db_path = db_path / "dump.sqlite"
        if not db_path.is_file():
            Path(db_path).touch()
        print(db_path)

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

    def get_unsanitized(self, session, all=True):
        query = session.query(RawEntry).filter_by(sanitized=False)
        if all:
            return query.all()
        return query.first()

    def get_by(self, model, key, val, session):
        return session.query(model).filter_by(**{key: val}).first()

    def delete_objects(self, to_delete_list, session):
        errors = 0
        for to_delete in to_delete_list:
            try:
                session.delete(to_delete)
            except Exception:
                errors += 1

        logger.info(f"Deleted {len(to_delete_list) - errors} entries")
        logger.error(f"Unsuccesfully deleted {errors} entries")


    def save_object(self, model, session):
        try:
            model.save(session)
            return True
        except Exception as e:
            logger.error(e)

        return False
