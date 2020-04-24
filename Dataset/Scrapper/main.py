import os
from datetime import datetime
from pathlib import Path

import Dataset.util.db.db_wrapper as db
from Dataset.Scrapper.Subreddits import ProgressPics, Brogress
from Dataset.util.db.model import RawEntry
from Dataset.util.dataset_logger import dataset_logger as logger
from Dataset.util.image_util import save_image, has_faces, check_duplicates
import argparse

p = Path.cwd() / 'dump'
db_wrapper = db.DBWrapper()

pimg = (p / 'img')
p.mkdir(parents=True, exist_ok=True)
pimg.mkdir(parents=True, exist_ok=True)
subreddits = [Brogress(), ProgressPics()]
stats = {}


def delete_files(to_delete_list):
    counter = 0
    for d in to_delete_list:
        try:
            os.remove(pimg / d)
            counter += 1
        except Exception:
            continue
    logger.info(f"Deleted {counter} entries")


def extract_features_from_api():
    for idx, subreddit in enumerate(subreddits):
        stats[subreddit.name] = {'correct': 0, 'error': 0}
        for idx2, (entry, post) in enumerate(subreddit.process()):

            if entry and db_wrapper.save_object(entry):
                stats[subreddit.name]['correct'] = stats[subreddit.name]['correct'] + 1
            else:
                stats[subreddit.name]['error'] = stats[subreddit.name]['error'] + 1
            if idx2 % 500 == 0 and idx2 != 0:
                logger.debug(f"{idx2} extracted from {subreddit.name}")


def download_images():
    to_delete = []
    for entry in RawEntry.query.filter_by("sanitized" == False).all():
        success, p = save_image(entry)
        updated = False
        if success:
            entry.local_url = p
            db_wrapper.save_object(entry)
        if not updated or not success:
            to_delete.append(entry)

    delete_files([e.local_url for e in to_delete])
    db_wrapper.delete_objects(to_delete)


def get_pictures_without_faces():
    logger.info("Checking faces")
    no_faces_list = []
    for index, fpath in enumerate(pimg.glob("**.jpg")):
        if fpath.is_file():
            try:
                if index % 200 == 0:
                    print(index)
                if not has_faces(fpath):
                    no_faces_list.append(fpath)
            except Exception as e:
                logger.error(e)
                no_faces_list.append(fpath)
    return no_faces_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", help="Delete duplicates/pictures without faces", type=bool)
    args = parser.parse_args()

    start_time = datetime.now()

    logger.error("Starting")
    extract_features_from_api()

    if args.clean:
        duplicates = check_duplicates()

        db_wrapper.delete_objects(table_name="raw_entry", filter_key="img_url", to_delete_list=duplicates)
        delete_files(duplicates)

        no_faces = get_pictures_without_faces()
        db_wrapper.delete_objects(table_name="raw_entry", filter_key="img_url", to_delete_list=no_faces)
        delete_files(no_faces)
        logger.info(f'Found {len(no_faces)} with no faces')

    logger.info(stats)

    logger.info("Checking for duplicates")

    logger.info(stats)
    strftime = "%H:%M:%S"
    end_time = datetime.now() - start_time
    logger.info(f"Took {end_time.strftime(strftime)} to complete")
