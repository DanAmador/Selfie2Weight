import argparse
from datetime import datetime
from multiprocessing.pool import ThreadPool
from pathlib import Path

from Scrapper.Subreddits import Brogress, ProgressPics
from util.dataset_logger import dataset_logger as logger
from util.db.Wrappers import MongoWrapper as db
from util.db.model import RawEntry
from util.image_util import save_image, check_duplicates, delete_file

p = Path.cwd() / 'dump'
db_wrapper = db.MongoWrapper()

pimg = (p / 'img')
p.mkdir(parents=True, exist_ok=True)
pimg.mkdir(parents=True, exist_ok=True)
subreddits = []
stats = {}


# Go through table and delete images and delete entries without a valid image
def download_raw_images(download_all=False):
    logger.info("Downloading Images")
    with db_wrapper.session_scope():
        query = RawEntry.objects if download_all else RawEntry.objects(local_path=None)

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

                    errors = 0
                    for success, path in results:
                        if success:
                            entry.local_path = str(path)
                            db_wrapper.save_object(entry)
                        else:
                            errors += 1
                            entry.delete()
                    total_errors += errors
                except Exception:
                    errors += len(urls)
                    logger.info(f'Whole batch crashed')
                    total_errors += errors
                finally:
                    logger.info(f'{errors} errors in the last batch {errors / len(urls)}')
                    urls = []

    logger.info(f'{errors} errors from {size} images ({errors / size})')


def extract_features_from_api():
    for idx, subreddit in enumerate(subreddits):
        stats[subreddit.name] = {'correct': 0, 'error': 0}
        for idx2, (entry, post) in enumerate(subreddit.process()):
            try:
                with db_wrapper.session_scope():
                    if entry and db_wrapper.save_object(entry):
                        stats[subreddit.name]['correct'] = stats[subreddit.name]['correct'] + 1
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

    logger.info("Running duplicate and face check")
    logger.info("Checking for duplicates")
    duplicates = check_duplicates()
    logger.info(f'Found {len(duplicates)} duplicates')
    e = sum([delete_file(d) for d in duplicates])
    logger.info(f"Deleted {len(duplicates) - e} entries in duplicates")
    logger.error(f"Unsuccesfully deleted {e} entries in duplicates")
    logger.info(stats)
    end_time = datetime.now() - start_time
    logger.info(f"Took {end_time} to complete")
