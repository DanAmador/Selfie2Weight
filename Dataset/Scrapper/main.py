import argparse
import os
from datetime import datetime
from pathlib import Path

from Dataset.Scrapper.Subreddits import Brogress, ProgressPics
from Dataset.util.dataset_logger import dataset_logger as logger
from Dataset.util.db.Wrappers import MongoWrapper as db

from Dataset.util.db.model import RawEntry
from Dataset.util.image_util import check_duplicates, download_raw_images, get_pictures_without_faces

p = Path.cwd() / 'dump'
db_wrapper = db.MongoWrapper()

pimg = (p / 'img')
p.mkdir(parents=True, exist_ok=True)
pimg.mkdir(parents=True, exist_ok=True)
subreddits = []
stats = {}


def update_sanitized(feature_metadata):
    logger.info(f"Updating {len(feature_metadata)}")
    error = 0

    for metadata in feature_metadata:
        reddit_id = metadata.pop("reddit_id")

        try:
            with db_wrapper.session_scope() as session:
                if metadata:
                    session.query(RawEntry).filter(RawEntry.reddit_id == reddit_id).update(metadata)
                    session.commit()
        except Exception as e:
            # logger.error(e)
            logger.error(f"Could not find entry {str(reddit_id)} and update it with {metadata}")
            error += 1
            continue

    logger.info(f"Correctly updated {len(feature_metadata) - error} from {len(feature_metadata)}")


def delete_files(to_delete):
    counter = 0
    errors = 0
    to_del_path = pimg / to_delete
    try:

        with db_wrapper.session_scope() as session:
            session.query(RawEntry).filter(RawEntry.local_path == str(to_del_path)).delete()
            if p.is_file():
                os.remove(p)
            session.commit()
            counter += 1
    except Exception as e:
        logger.error(e)
        errors += 1

    return errors


def extract_features_from_api():
    for idx, subreddit in enumerate(subreddits):
        stats[subreddit.name] = {'correct': 0, 'error': 0}
        for idx2, (entry, post) in enumerate(subreddit.process()):
            try:
                with db_wrapper.session_scope() as session:
                    if entry and db_wrapper.save_object(entry, session=session):
                        stats[subreddit.name]['correct'] = stats[subreddit.name]['correct'] + 1
                        session.commit()
                    else:
                        stats[subreddit.name]['error'] = stats[subreddit.name]['error'] + 1
                    if idx2 % 500 == 0 and idx2 != 0:
                        logger.debug(f"{idx2} extracted from {subreddit.name}")
            except Exception as e:
                logger.error(e)
                stats[subreddit.name]['error'] = stats[subreddit.name]['error'] + 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--meta", help="Download metadata from subreddits", type=bool, default=True)
    parser.add_argument("--images", help="Download images", type=bool, default=True)
    parser.add_argument("--clean", help="Delete duplicates/pictures without faces", type=bool, default=True)
    args = parser.parse_args()

    start_time = datetime.now()

    logger.info("Starting")
    if args.meta:
        logger.info("Running metadata download")
        subreddits = [ProgressPics(), Brogress()]
        extract_features_from_api()
    if args.images:
        logger.info("Downloading raw images from metadata")
        download_raw_images()

    if args.clean:
        logger.info("Running duplicate and face check")
        logger.info("Checking for duplicates")
        duplicates = check_duplicates()
        logger.info(f'Found {len(duplicates)} duplicates')
        e = sum([delete_files(d) for d in duplicates])
        logger.info(f"Deleted {len(duplicates) - e} entries in duplicates")
        logger.error(f"Unsuccesfully deleted {e} entries in duplicates")

        logger.info("Face check")
        no_faces, feature_metadata = get_pictures_without_faces()
        update_sanitized(feature_metadata)
        logger.info(f'Found {len(no_faces)} with no faces')
        e = sum([delete_files(d) for d in no_faces])

        logger.info(f"Deleted {len(no_faces) - e} entries in no face")
        logger.error(f"Unsuccesfully deleted {e} entries in duplicates")

        logger.info(stats)

    end_time = datetime.now() - start_time
    logger.info(f"Took {end_time} to complete")
