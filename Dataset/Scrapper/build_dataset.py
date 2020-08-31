import json
from pathlib import Path

from PIL import Image

from util.dataset_logger import dataset_logger as logger
from util.db.Wrappers import MongoWrapper as db
from util.db.model import RawEntry, SanitizedEntry

p = Path(__file__).parent / 'dump' / "dataset"
sanimg = p / "images"

db_wrapper = db.MongoWrapper()


def crop_image(img: Image, meta: SanitizedEntry, idx: int):
    name = f'{meta.reddit_id}_{str(meta.weight).replace(".", "-")}_{meta.age}_{idx}.jpg'
    new_path = sanimg / name
    img.crop(meta.bounding_box.to_tuple()).save(new_path)
    return new_path


def get_features_in_crop(r: RawEntry, s: SanitizedEntry):
    for key, metas in r.raw_meta.items():
        crop_features = set()
        for m in metas:

            res = s.bounding_box.contains(m.bounding_box)
            if res:
                crop_features.add(key)
        return list(crop_features)


if __name__ == "__main__":
    if not sanimg.is_dir():
        sanimg.mkdir(parents=True, exist_ok=True)
    metadata = []
    errors = 0
    with db_wrapper.session_scope():
        for r in RawEntry.objects(has_been_sanitized=True):
            try:

                img = Image.open(r.local_path)

                for idx, s in enumerate(r.sanitized_entries):
                    img_path = crop_image(img, s, idx)
                    obj = {
                        "weight": float(s.weight),
                        "age": s.age,
                        "sex": r.sex,
                        "reddit_id": r.reddit_id,
                        "features": get_features_in_crop(r, s),
                        "path": img_path.name
                    }
                    metadata.append(obj)
            except Exception as e:
                logger.error(f"{img_path} crashed with {e}")
                errors += 1
        logger.info(f"Had {errors} errors")
        with open(p / "meta.json", "w") as d:
            json.dump(metadata, d)
