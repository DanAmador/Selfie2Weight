import hashlib
import os
from pathlib import Path
from typing import List
from multiprocessing.pool import ThreadPool
import cv2
import requests
import Dataset.util.db.db_wrapper as db
from Dataset.util.dataset_logger import dataset_logger as logger
from Dataset.util.db.model import RawEntry

db_wrapper = db.DBWrapper()

faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
p = Path.cwd() / 'dump'
pimg = (p / 'img')


def save_image(raw_entry: RawEntry):
    # try:
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


# Go through table and delete images and delete entries without a valid image
def download_raw_images(download_all=False):
    query = {}
    logger.info("Downloading Images")
    with db_wrapper.session_scope() as session:
        session.expire_on_commit = False
        query = session.query(RawEntry).all() if download_all else db_wrapper.get_by(RawEntry, "local_path", None,
                                                                                     session=session, only_first=False)

    logger.info(f"Starting download from {len(query)} images")
    urls = []
    for idx, entry in enumerate(query):
        urls.append(entry)
        if len(urls) >= 10 or idx - 1 == len(query):
            results = ThreadPool(8).imap_unordered(save_image, urls)
            urls = []
            with db_wrapper.session_scope() as session:
                for success, path in results:
                    if success:
                        entry.local_path = str(path)
                        db_wrapper.save_object(entry, session)
                    else:
                        session.delete(entry)
                        session.commit()


