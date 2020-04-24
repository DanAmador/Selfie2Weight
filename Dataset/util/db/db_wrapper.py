import sqlite3
from pathlib import Path

from sqlalchemy.orm import sessionmaker

from Dataset.util.dataset_logger import dataset_logger as logger
from sqlalchemy import create_engine

from Dataset.util.db.base_class import Base

p = Path().cwd().parent / "Scrapper" / 'dump'


class DBWrapper:
    def __init__(self, db_path=p) -> None:
        db_path = db_path / "dump.sqlite"
        if not db_path.is_file():
            Path(db_path).touch()
        print(db_path)

        engine = create_engine(f"sqlite:///{db_path}")
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.session = Session()
        Base.metadata.create_all(bind=engine)

    #
    # def start_tables(self):
    #
    #     create_sanitized_table = """ CREATE TABLE IF NOT EXISTS sanitized (
    #                                             reddit_id TEXT NOT NULL,
    #                                             id TEXT PRIMARY KEY,
    #                                             sex char NOT NULL,
    #                                             age INTEGER NOT NULL,
    #                                             height REAL NOT NULL,
    #                                             weight REAL NOT NULL
    #                                         ); """
    #
    #     create_raw_table = """ CREATE TABLE IF NOT EXISTS raw_entry (
    #                                             sex char NOT NULL,
    #                                             age INTEGER NOT NULL,
    #                                             height REAL NOT NULL,
    #                                             start_weight REAL NOT NULL,
    #                                             end_weight REAL NOT NULL,
    #                                             reddit_id TEXT NOT NULL,
    #                                             img_url TEXT NOT NULL,
    #                                             local_url TEXT,
    #                                             sanitized INTEGER default 0
    #                                         ); """
    #     try:
    #
    #         c = self.conn.cursor()
    #         c.execute(create_raw_table)
    #         c.execute(create_sanitized_table)
    #     except Exception as e:
    #         logger.error(f" Error at db wrapper {str(e)}")

    def update(self, dataclass):
        with self.conn:
            columns, values = self._info_from_dataclass(dataclass)
            set_str = ",".join([f"{c} = v" for c, v in zip(columns, values)])
            update_str = f"UPDATE {dataclass.tablename} set {set_str} where id = {dataclass.id}"

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
