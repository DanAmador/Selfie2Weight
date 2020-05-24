import hashlib
import os
from multiprocessing.pool import ThreadPool, Pool
from pathlib import Path
from typing import List, Dict, Tuple

import cv2
import requests
from collections import namedtuple

from util.db.Wrappers import MongoWrapper as db
from util.dataset_logger import dataset_logger as logger
from util.db.model import RawEntry

db_wrapper = db.MongoWrapper()

FaceMeta = namedtuple("FaceMeta", "frontalface profileface upperbody")
p = Path.cwd() / 'dump'
cascades_classifiers = {str(e).split(".xml")[0].split("haarcascade_")[1]: cv2.CascadeClassifier(str(e)) for e in
                        p.parent.parent.rglob("cascades/*.xml")}
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


def does_not_have_faces(img_path) -> Dict[str, bool]:
    face_meta = {"path": img_path}
    if img_path.is_file():
        total_detected = 0
        image = cv2.imread(img_path.as_posix(), 0)
        for name, cascade in cascades_classifiers.items():
            faces = cascade.detectMultiScale(
                image,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            if len(faces) > 0:
                face_meta[name] = True
            total_detected += len(faces)
        del image
    return face_meta


def get_pictures_without_faces() -> Tuple[List[str], List[Dict]]:
    logger.info("Checking faces")
    no_faces_list = []
    feature_list = []
    index = 0
    results = Pool().imap_unordered(does_not_have_faces, pimg.glob("**/*.jpg"))
    for meta in results:
        index += 1
        fpath = meta.pop("path")
        no_face = True
        try:
            if index % 200 == 10:
                logger.info(f"{index}  analyzed and {len(no_faces_list)} have no faces so far ")
            if "frontalface_default" in meta.keys() or "profileface" in meta.keys():
                no_face = False
            meta["reddit_id"] = fpath.name.split(".")[0]
            if no_face:
                no_faces_list.append(fpath)
            else:
                feature_list.append(meta)
        except Exception as e:
            logger.error(e)
            no_faces_list.append(fpath)
    return no_faces_list, feature_list


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
    total_errors = 0
    size = len(query)
    current = 0
    for idx, entry in enumerate(query):
        urls.append(entry)
        if len(urls) >= 300 or idx - 1 == size:
            logger.info(f'Downloading images {current} to {idx} from {size}')
            current = idx
            try:
                results = ThreadPool(8).imap_unordered(save_image, urls)

                with db_wrapper.session_scope() as session:
                    errors = 0
                    for success, path in results:
                        if success:
                            entry.local_path = str(path)
                            db_wrapper.save_object(entry, session)
                        else:
                            errors += 1
                            session.delete(entry)
                    total_errors += errors
                    session.commit()
            except Exception:
                errors += len(urls)
                logger.info(f'Whole batch crashed')
                total_errors += errors
            finally:
                logger.info(f'{errors} errors in the last batch {errors / len(urls)}')
                urls = []

    logger.info(f'{errors} errors from {size} images ({errors / size})')
