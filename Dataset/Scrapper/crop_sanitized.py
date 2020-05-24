from pathlib import Path
import Dataset.util.db.SQLWrapper as db
from Dataset.util.db.model import SanitizedEntry, RawEntry

from PIL import Image

p = Path.cwd() / 'dump'
sanimg = p / "sanitized"
db_wrapper = db.SQLWrapper()


def crop_image(img: Image, meta: SanitizedEntry, session):
    tup = (meta.x, meta.y, meta.x + meta.width, meta.y + meta.height)
    name = f'{meta.reddit_id}_{str(meta.weight).replace(".", "-")}.jpg'
    new_path = sanimg / name
    img.crop(tup).save(new_path)
    meta.local_path = str(new_path)
    db_wrapper.save_object(meta, session)


if __name__ == '__main__':
    if not sanimg.is_dir():
        sanimg.mkdir(parents=True, exist_ok=True)
    with db_wrapper.session_scope() as session:
        for raw in session.query(RawEntry).join(RawEntry.sanitized_entries).filter(
                RawEntry.local_path != None).all():
            print(raw.sanitized_entries)
            img = Image.open(raw.local_path)

            for sanitized in raw.sanitized_entries:
                crop_image(img, sanitized, session)
                print(sanitized.as_dict)
