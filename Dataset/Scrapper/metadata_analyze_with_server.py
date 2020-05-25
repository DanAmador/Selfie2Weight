from pathlib import Path
from typing import Dict

import cv2
import imutils
import requests

from util.dataset_logger import dataset_logger as logger

p = Path.cwd() / 'dump'
cascades_classifiers = {str(e).split(".xml")[0].split("haarcascade_")[1]: cv2.CascadeClassifier(str(e)) for e in
                        p.parent.parent.rglob("cascades/*.xml")}
pimg = (p / 'img')
host = "http://192.168.0.115:5000"


def analyze_single_image(img_path) -> Dict[str, bool]:
    face_meta = {}
    image = imutils.url_to_image(f"{host}{img_path}")
    for name, cascade in cascades_classifiers.items():
        faces = cascade.detectMultiScale(
            image,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        if len(faces) > 0:
            face_meta[name] = True
    del image
    return face_meta


def not_preprocessed_generator():
    next_str = "/next/was_preprocessed"

    res = requests.get(f"{host}{next_str}")
    last = {}
    while res.status_code != 204:
        current = res.json()
        yield current
        if last == current:
            break
        last = current
        res = requests.get(f"{host}{next_str}")


def analyze_cascades_from_api():
    logger.info("Checking faces")
    no_face_counter = 0

    img_gen = not_preprocessed_generator()
    for index, doc in enumerate(img_gen):
        fpath = doc.get("img_url", None)
        reddit_id = doc.get("reddit_id", None)
        if fpath and reddit_id:
            meta = analyze_single_image(fpath)
            no_face = True
            try:
                if index % 200 == 10:
                    if no_face_counter > 0:
                        logger.info(
                            f"{index}  analyzed and {no_face_counter} have no faces so far {index / no_face_counter}")
                if "frontalface_default" in meta.keys() or "profileface" in meta.keys():
                    no_face = False
                meta["reddit_id"] = reddit_id
                if no_face:
                    no_face_counter += 1
                    requests.post(f"{host}/img/{reddit_id}")
                else:
                    update_sanitized(reddit_id, meta)
            except Exception as e:
                logger.error(e)
    logger.info(f'Found {no_face_counter} with no faces')


def update_sanitized(reddit_id, feature_metadata):
    try:
        res = requests.post(f"{host}/meta/{reddit_id}", data=feature_metadata)
    except Exception as e:
        # logger.error(e)
        logger.error(f"Could not find entry {str(reddit_id)} and update it with {feature_metadata}")
        return False
    return True


if __name__ == "__main__":
    logger.info("Face check")
    analyze_cascades_from_api()
