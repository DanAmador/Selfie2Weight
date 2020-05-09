import argparse
import os
from datetime import datetime
from pathlib import Path

import Dataset.util.db.db_wrapper as db
from Dataset.Scrapper.Subreddits import ProgressPics, Brogress
from Dataset.util.dataset_logger import dataset_logger as logger
from Dataset.util.db.model import RawEntry
from Dataset.util.image_util import save_image, has_faces, check_duplicates, download_raw_images

p = Path.cwd() / 'dump'
db_wrapper = db.DBWrapper()

pimg = (p / 'img')
p.mkdir(parents=True, exist_ok=True)
pimg.mkdir(parents=True, exist_ok=True)
subreddits = [Brogress(), ProgressPics()]
stats = {}


def delete_files(to_delete_list, session):
    counter = 0
    errors = 0
    for d in to_delete_list:
        try:
            session.query(RawEntry).filter(RawEntry.local_path == str(pimg / d)).delete()
            os.remove(pimg / d)
            session.commit()
            counter += 1
        except Exception:
            errors += 1
            continue

    logger.info(f"Deleted {len(to_delete_list) - errors} entries")
    logger.error(f"Unsuccesfully deleted {errors} entries")


def extract_features_from_api():
    with db_wrapper.session_scope() as session:
        for idx, subreddit in enumerate(subreddits):
            stats[subreddit.name] = {'correct': 0, 'error': 0}
            for idx2, (entry, post) in enumerate(subreddit.process()):

                if entry and db_wrapper.save_object(entry, session=session):
                    stats[subreddit.name]['correct'] = stats[subreddit.name]['correct'] + 1
                else:
                    stats[subreddit.name]['error'] = stats[subreddit.name]['error'] + 1
                if idx2 % 500 == 0 and idx2 != 0:
                    logger.debug(f"{idx2} extracted from {subreddit.name}")


def get_pictures_without_faces():
    logger.info("Checking faces")
    no_faces_list = []
    for index, fpath in enumerate(pimg.glob("**/*.jpg")):
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
    parser.add_argument("--clean", help="Delete duplicates/pictures without faces", type=bool, default=True)
    parser.add_argument("--images", help="Download images", type=bool, default=True)
    args = parser.parse_args()

    start_time = datetime.now()

    logger.info("Starting")
    extract_features_from_api()
    if args.images:
        with db_wrapper.session_scope() as session:
            download_raw_images(session)

    if args.clean:
        duplicates = check_duplicates()
        with db_wrapper.session_scope() as session:
            delete_files(duplicates, session)

            no_faces = get_pictures_without_faces()
            delete_files(no_faces, session)
    logger.info(f'Found {len(no_faces)} with no faces')

    logger.info(stats)

    logger.info("Checking for duplicates")

    logger.info(stats)
    end_time = datetime.now() - start_time
    logger.info(f"Took {end_time} to complete")
