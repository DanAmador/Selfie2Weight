from pathlib import Path
from PIL import Image

from util.db.model import RawEntry, SanitizedEntry
from util.db.Wrappers import MongoWrapper as db

p = Path(__file__).parent / 'dump'
sanimg = p / "sanitized"

db_wrapper = db.MongoWrapper()


def crop_image(img: Image, meta: SanitizedEntry, idx: int):
    tup = (meta.x, meta.y, meta.x + meta.width, meta.y + meta.height)
    name = f'{meta.reddit_id}_{str(meta.weight).replace(".", "-")}_{meta.age}_{idx}.jpg'
    new_path = sanimg / name
    img.crop(tup).save(new_path)
    return new_path


if __name__ == "__main__":
    if not sanimg.is_dir():
        sanimg.mkdir(parents=True, exist_ok=True)
    metadata = []
    with db_wrapper.session_scope():

        for r in RawEntry.objects(has_been_sanitized=True):
            img = Image.open(r.local_path)

            for idx, s in enumerate(r.sanitized_entries):
                img_path = crop_image(img, s, idx)
