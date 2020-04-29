import hashlib
import urllib
from pathlib import Path
import logging
from typing import List

import cv2
import os

from .db.model import RawEntry
from .dataset_logger import dataset_logger as logger
import Dataset.util.db.db_wrapper as db

db_wrapper = db.DBWrapper()

faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
p = Path.cwd() / 'dump'
pimg = (p / 'img')


def save_image(raw_entry: RawEntry):
    try:
        if raw_entry.img_url.endswith(".jpg"):
            response = urllib.request.urlopen(raw_entry.img_url)
            img = response.read()

            name = str(raw_entry.reddit_id) + '.jpg'
            pimg = Path.cwd() / 'dump' / 'img'
            if not pimg.is_dir():
                pimg.mkdir(parents=True, exist_ok=True)
            with open(pimg / name, 'wb') as f:
                f.write(img)
                return True, pimg / name
        return False, None
    except Exception as e:
        # logging.getLogger('crawler').error(e)
        return False, None


def check_duplicates() -> List[str]:
    hash_keys = {}
    duplicates = []
    for index, filename in enumerate(os.listdir(pimg)):
        if (pimg / filename).is_file():
            try:
                with open(pimg / filename, 'rb') as f:
                    if index % 1000 == 0:
                        print(index)
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


def has_faces(img_path) -> bool:
    image = cv2.imread(img_path.as_posix(), 0)
    faces = faceCascade.detectMultiScale(
        image,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    return len(faces) == 0


# TODO download images from cropData table
def download_raw_images(session):
    for entry in db_wrapper.get_by(RawEntry, "local_path", None, session=session, only_first=False):
        succ, p = save_image(entry)
        if succ:
            entry.local_path = str(p)
            db_wrapper.save_object(entry, session)