import urllib
from collections import namedtuple
from pathlib import Path
import logging
Entry = namedtuple("Entry", "sex age height start_weight end_weight id sanitized path")


def save_image(post):
    try:
        if post.url.endswith(".jpg"):
            response = urllib.request.urlopen(post.url)
            img = response.read()

            name = str(post.id) + '.jpg'
            pimg = Path.cwd() / 'dump' / 'img'
            pimg.touch(name)
            with open(pimg / name, 'wb') as f:
                f.write(img)
                return True
        return False
    except Exception as e:
        # logging.getLogger('crawler').error(e)
        return False
