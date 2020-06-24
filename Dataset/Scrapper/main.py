import argparse
import json
import sys
from datetime import datetime
from multiprocessing.pool import ThreadPool
from pathlib import Path
import os


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
        query = RawEntry.objects(has_image=False)

        logger.info(f"Starting download from {len(query)} images")
        total_errors = 0
        size = len(query) if len(query) != 0 else None
        current = 0
        for idx, entry in enumerate(query):
            if idx % 300 == 1 or idx - 1 == size:
                logger.info(f'Downloading images {current} to {idx} from {size}')
                current = idx
            try:
                success, path = save_image(entry)
                if success and Path(path).is_file():
                    entry.local_path = str(path)
                    entry.has_image = True
                    db_wrapper.save_object(entry)
                else:
                    entry.delete()
                    total_errors += 1
            except Exception as e:
                logger.error(f'Whole batch crashed')
                logger.error(e)
                total_errors += 1

        if size:
            logger.info(f'{total_errors} errors found in {len(query)}  which is {total_errors / size}')


def extract_features_from_api(limit=sys.maxsize):
    for idx, subreddit in enumerate(subreddits):

        stats[subreddit.name] = {'correct': 0, 'error': 0}
        for idx2, (entry, post) in enumerate(subreddit.process()):
            if idx2 > limit:
                return
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


def double_check_files():
    logger.info("Double checking files")
    correct = 0
    no_file = 0
    total = 0
    with db_wrapper.session_scope():
        for total, raw in enumerate(RawEntry.objects):
            if total % 100 == 1:
                logger.info(f"{no_file} from {total} so far have no file  {(no_file / total) * 100}'")
            try:
                if raw.local_path and not Path(raw.local_path).is_file():
                    p = raw.local_path
                    success, path = save_image(raw)
                    if not success or not Path(path).is_file():
                        raw.delete()
                        os.remove(p)
                else:
                    no_file += 1

                    raw.delete()
            except Exception as e:
                no_file += 1
                logger.error(f"Error at deleting {raw.reddit_id}: {e}")
            finally:
                correct += 1
        logger.info(f"{correct} from {total} correct {(correct / total) * 100}'")
        logger.info(f"{no_file} from {total} has no file  {(correct / total) * 100}'")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--meta", help="Download metadata from subreddits", type=bool, default=False)
    parser.add_argument("--images", help="Download images", type=bool, default=False)
    parser.add_argument("--double_check", help="Double check", type=bool, default=False)
    args = parser.parse_args()

    start_time = datetime.now()
    logger.info("Starting")
    if args.meta:
        d = Path(__file__).parent / "dump/db.json"
        if d.is_file():
            not_unique = 0
            with open(d) as j:
                jayson = json.load(j)
                with db_wrapper.session_scope():
                    for idx, raw_entry in enumerate(jayson):
                        if idx % 500 == 1:
                            logger.info(f"Saved {idx} raw entries from json dump with {not_unique} not unique")
                        r = RawEntry.from_json(json.dumps(raw_entry))
                        r.has_image = False
                        r.local_path = ""
                        succ = db_wrapper.save_object(r)
                        if not succ:  # :(
                            not_unique += 1
        else:
            from Scrapper.Subreddits import Brogress, ProgressPics

            logger.info("Running metadata download")
            subreddits = [ProgressPics(), Brogress()]
            extract_features_from_api()
    if args.images:
        logger.info("Resetting image download")
        with db_wrapper.session_scope():
            for r in RawEntry.objects(has_image=True):
                try:
                    os.remove(r.local_path)
                except Exception:
                    logger.error(f"{r.reddit_id} didn't have an image")
                finally:
                    r.local_path = ""
                    r.has_image = False
                    r.save()
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

    if args.double_check:
        double_check_files()

    end_time = datetime.now() - start_time
    logger.info(f"Took {end_time} to complete")
