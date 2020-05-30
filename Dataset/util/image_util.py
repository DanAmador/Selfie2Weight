import hashlib
import os
from pathlib import Path
from typing import List

import requests

from util.dataset_logger import dataset_logger as logger
from util.db.Wrappers import MongoWrapper as db
from util.db.model import RawEntry

db_wrapper = db.MongoWrapper()

p = Path.cwd() / 'dump'
pimg = (p / 'img')


def delete_file(to_delete: Path):
    counter = 0
    errors = 0
    to_del_path = pimg / to_delete
    try:
        with db_wrapper.session_scope():
            RawEntry.objects(local_path=str(to_del_path)).delete()
            if to_del_path.is_file():
                os.remove(to_del_path)
            counter += 1
    except Exception as e:
        logger.error(e)
        errors += 1

    return errors


def save_image(raw_entry: RawEntry):
    if raw_entry.img_url.endswith(".jpg"):
        r = requests.get(raw_entry.img_url, stream=True)
        if r.status_code == 200:
            name = str(raw_entry.reddit_id) + '.jpg'
            pimg = Path.cwd() / 'dump' / 'img'
            if not pimg.is_dir():
                pimg.mkdir(parents=True, exist_ok=True)
            with open(pimg / name, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
            return True, pimg / name
    return False, None


def check_duplicates() -> List[str]:
    hash_keys = {}
    duplicates = []
    for index, filename in enumerate(os.listdir(pimg)):
        if (pimg / filename).is_file():
            try:
                with open(pimg / filename, 'rb') as f:
                    if index % 1000 == 0:
                        logger.info(f"{index}  analyzed and {len(duplicates)} are duplicates ")

                    filehash = hashlib.md5(f.read()).hexdigest()

                    if filehash not in hash_keys:
                        hash_keys[filehash] = filename
                    else:
                        duplicates.append(filename)
            except Exception as e:
                logger.error(e)
                duplicates.append(filename)
    logger.info(f'Found {len(duplicates)} duplicates')

    return duplicates
