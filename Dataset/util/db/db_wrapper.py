import sqlite3
from pathlib import Path

from sqlalchemy.orm import sessionmaker

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
        self.SessionClass = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.session = self.SessionClass()
        Base.metadata.create_all(bind=engine)

    def get_unsanitized(self):
        return self.session.query(RawEntry).filter_by(sanitized=False).all()

    def get_by(self, model, key, val):
        return self.session.query(model).filter_by({key: val})

    def delete_objects(self, to_delete_list):
        errors = 0
        for to_delete in to_delete_list:
            try:
                self.session.delete(to_delete)
            except Exception:
                errors += 1

        logger.info(f"Deleted {len(to_delete_list) - errors} entries")
        logger.error(f"Unsuccesfully deleted {errors} entries")

    def save_object(self, model):
        try:
            model.save(self.session)
            return True
        except Exception as e:
            logger.error(e)
        return False
