import urllib
from pathlib import Path
from typing import Dict, Tuple, List

import numpy as np
import requests
import cv2

from util.dataset_logger import dataset_logger as logger
from util.db.Wrappers import MongoWrapper as db
from util.db.model import RawEntry
from util.image_util import delete_file

p = Path.cwd() / 'dump'
db_wrapper = db.MongoWrapper()
cascades_classifiers = {str(e).split(".xml")[0].split("haarcascade_")[1]: cv2.CascadeClassifier(str(e)) for e in
                        p.parent.parent.rglob("cascades/*.xml")}
pimg = (p / 'img')
host = "localhost:5000"


# METHOD #1: OpenCV, NumPy, and urllib
def url_to_image(url):
    # download the image, convert it to a NumPy array, and then read
    # it into OpenCV format
    resp = urllib.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    # return the image
    return image


def does_not_have_faces(img_path) -> Dict[str, bool]:
    face_meta = {"path": img_path}
    if img_path.is_file():
        total_detected = 0
        image = url_to_image(img_path)
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


def get_image():
    next_str = "/next/was_preprocessed"

    res = requests.get(f"{host}{next_str}")
    while res.status_code != 204:
        yield res.json()

        res = requests.get(f"{host}{next_str}")


def get_pictures_without_faces() -> Tuple[List[str], List[Dict]]:
    logger.info("Checking faces")
    no_faces_list = []
    feature_list = []
    index = 0
    img_gen = get_image()
    for doc in img_gen:
        index += 1
        meta = does_not_have_faces(doc.get("local_path"), None)
        if meta:
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


def update_sanitized(feature_metadata):
    logger.info(f"Updating {len(feature_metadata)}")
    error = 0

    for metadata in feature_metadata:
        reddit_id = metadata.pop("reddit_id")

        try:
            with db_wrapper.session_scope():
                if metadata:
                    ro: RawEntry = RawEntry.objects(reddit_id=reddit_id).first()
                    ro.raw_meta = metadata
                    db_wrapper.save_object(ro)
        except Exception as e:
            # logger.error(e)
            logger.error(f"Could not find entry {str(reddit_id)} and update it with {metadata}")
            error += 1
            continue

    logger.info(f"Correctly updated {len(feature_metadata) - error} from {len(feature_metadata)}")


if __name__ == "__main__":
    logger.info("Face check")
    no_faces, feature_metadata = get_pictures_without_faces()
    update_sanitized(feature_metadata)
    logger.info(f'Found {len(no_faces)} with no faces')
    e = sum([delete_file(d) for d in no_faces])

    logger.info(f"Deleted {len(no_faces) - e} entries in no face")
    logger.error(f"Unsuccesfully deleted {e} entries in duplicates")
