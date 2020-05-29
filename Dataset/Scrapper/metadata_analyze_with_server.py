from pathlib import Path
from typing import Dict

import cv2
import imutils
import requests
from datetime import datetime

from util.dataset_logger import dataset_logger as logger

p = Path.cwd() / 'dump'
cascades_classifiers = {str(e).split(".xml")[0].split("haarcascade_")[1]: cv2.CascadeClassifier(str(e)) for e in
                        p.parent.parent.rglob("cascades/*.xml")}
pimg = (p / 'img')
host = "http://192.168.0.115:5000"


def analyze_single_image(img_path) -> Dict[str, bool]:
    face_meta = {}
    url = f"{host}{img_path}"
    image = imutils.url_to_image(url)
    for name, cascade in cascades_classifiers.items():
        faces = cascade.detectMultiScale(
            image,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        if len(faces) > 0:
            m = []
            for (x, y, w, h) in faces:
                m.append({"x": int(x), "y": int(y), "width": int(w), "height": int(h)})
            face_meta[name] = m
    del image
    return face_meta


def not_preprocessed_generator():
    next_str = "/next/was_preprocessed"

    res = requests.get(f"{host}{next_str}")
    while res.status_code != 204:
        current = res.json()
        yield current
        res = requests.get(f"{host}{next_str}")


def analyze_cascades_from_api():
    logger.info("Checking faces")
    no_face_counter = 0
    face_counter = 0
    img_gen = not_preprocessed_generator()
    for index, doc in enumerate(img_gen):
        fpath = doc.get("img_url", None)
        reddit_id = doc.get("reddit_id", None)
        if fpath and reddit_id and "local_path" in doc:
            meta = analyze_single_image(fpath)
            no_face = True
            try:
                if index % 100 == 10:
                    logger.info(
                        f"{index}  analyzed and {no_face_counter} have no faces so far {no_face_counter / index}")
                if "frontalface_default" in meta.keys() or "profileface" in meta.keys():
                    no_face = False
                if no_face:
                    no_face_counter += 1
                    requests.post(f"{host}/img/{reddit_id}")
                else:
                    face_counter += 1
                    update_meta(reddit_id, meta)
            except Exception as e:
                logger.error(e)
    logger.info(f'Found {no_face_counter} with no faces')
    logger.info(f'Found {face_counter} with faces!! :D')


def update_meta(reddit_id, feature_metadata):
    try:
        res = requests.post(f"{host}/meta/{reddit_id}", json=feature_metadata)
    except Exception as e:
        logger.error(e)
        logger.error(f"Could not find entry {str(reddit_id)} and update it with {feature_metadata}")
        return False
    return True


if __name__ == "__main__":
    logger.info("Face check")
    start_time = datetime.now()

    analyze_cascades_from_api()
    end_time = datetime.now() - start_time
    logger.info(f"Took {end_time} to complete")
