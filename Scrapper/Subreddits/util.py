import urllib
from collections import namedtuple
from pathlib import Path

Entry = namedtuple("Entry", "sex age height start_weight end_weight id sanitized")


def save_image(post):
    try:
        response = urllib.request.urlopen(post.url)
        img = response.read()

        name = str(post.id) + '.jpg'
        pimg = Path.cwd() / 'dump' / 'img'
        pimg.touch(name)
        with open(pimg / name, 'wb') as f:
            f.write(img)
            return True
    except Exception:
        return False