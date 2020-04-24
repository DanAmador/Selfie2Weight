import sqlite3
from pathlib import Path

from Dataset.util.dataset_logger import dataset_logger as logger

p = Path().cwd().parent / "Scrapper" / 'dump'


class DBWrapper:
    def __init__(self, db_path=p / "dump.sqlite") -> None:
        if not db_path.is_file():
            db_path.touch()
        self.conn = sqlite3.connect(db_path)
        self.start_tables()

    def start_tables(self):

        create_sanitized_table = """ CREATE TABLE IF NOT EXISTS sanitized (
                                                reddit_id TEXT NOT NULL,
                                                id TEXT PRIMARY KEY,
                                                sex char NOT NULL,
                                                age INTEGER NOT NULL, 
                                                height REAL NOT NULL,
                                                weight REAL NOT NULL
                                            ); """

        create_raw_table = """ CREATE TABLE IF NOT EXISTS raw_entry (
                                                reddit_id TEXT NOT NULL,
                                                sex char NOT NULL,
                                                age INTEGER NOT NULL, 
                                                height REAL NOT NULL,
                                                start_weight REAL NOT NULL,
                                                end_weight REAL NOT NULL,
                                                local_url TEXT,
                                                img_url TEXT NOT NULL,
                                                sanitized INTEGER default 0
                                            ); """
        try:

            c = self.conn.cursor()
            c.execute(create_raw_table)
            c.execute(create_sanitized_table)
        except Exception as e:
            logger.error(f" Error at db wrapper {str(e)}")

    def delete_by(self, table_name, filter_key, to_delete_list):
        for to_delete in to_delete_list:
            delete_statement = f"""DELETE FROM {table_name} WHERE {filter_key} = {to_delete}"""
            print(delete_statement)
            self.conn.execute(delete_statement)
        logger.info(f"Deleted {len(to_delete)} entries")

    # I just wish python had better types...
    def insert_into(self, dataclass_instance):
        available_attributes = []
        values = []
        for key in dataclass_instance.__annotations__.keys():
            val = getattr(dataclass_instance, key)
            if val:
                available_attributes.append(key)
                if type(val) == str:
                    values.append(f"'{val}'")
                else:
                    values.append(str(val))
        columns = ",".join(available_attributes)
        values = ",".join(values)
        insert_statement = f"INSERT INTO {dataclass_instance} ({columns}) VALUES ({values})"

        with self.conn:
            self.conn.execute(insert_statement)
