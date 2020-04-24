import os
from datetime import datetime
from pathlib import Path

import Dataset.util.db_wrapper as db
from Dataset.Scrapper.Subreddits import ProgressPics, Brogress
from Dataset.util.data_classes import RawEntry
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
    for d in to_delete_list:
        os.remove(pimg / d)
    logger.info(f"Deleted {len(to_delete_list)} entries")


def extract_features_from_api(image_save_flag=True):
    for idx, subreddit in enumerate(subreddits):
        stats[subreddit.name] = {'correct': 0, 'error': 0}
        for idx2, (entry, post) in enumerate(subreddit.process()):
            image, local_img_path = save_image(post) if image_save_flag else (True, None)

            if entry and image:
                db_wrapper.insert_into(dataclass_instance=entry)
                stats[subreddit.name]['correct'] = stats[subreddit.name]['correct'] + 1
            else:
                stats[subreddit.name]['error'] = stats[subreddit.name]['error'] + 1
            if idx2 % 500 == 0 and idx2 != 0:
                logger.debug(f"{idx2} from {subreddit.name}")


def get_pictures_without_faces():
    logger.info("Checking faces")
    no_faces_list = []
    for index, filename in enumerate(os.listdir(pimg)):
        fpath = pimg / filename
        if fpath.is_file():
            try:
                if index % 200 == 0:
                    print(index)
                if not has_faces(fpath):
                    no_faces_list.append(filename)
            except Exception as e:
                logger.error(e)
                no_faces_list.append(filename)
    return no_faces_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", help="Save images", type=bool)
    parser.add_argument("--clean", help="Delete duplicates/pictures without faces", type=bool)
    args = parser.parse_args()

    start_time = datetime.now()

    logger.error("Starting")
    extract_features_from_api()

    if args.clean:
        duplicates = check_duplicates()

        db_wrapper.delete_by(table_name="raw_entry", filter_key="img_url", to_delete_list=duplicates)
        delete_files(duplicates)

        no_faces = get_pictures_without_faces()
        db_wrapper.delete_by(table_name="raw_entry", filter_key="img_url", to_delete_list=no_faces)
        delete_files(no_faces)
        logger.info(f'Found {len(no_faces)} with no faces')

    logger.info(stats)

    logger.info("Checking for duplicates")

    logger.info(stats)
    strftime = "%H:%M:%S"
    end_time = datetime.now() - start_time
    logger.info(f"Took {end_time.strftime(strftime)} to complete")
