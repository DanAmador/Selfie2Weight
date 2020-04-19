import csv
import hashlib
import os
from pathlib import Path
import cv2
from Scrapper.Subreddits.Brogress import Brogress
from Scrapper.Subreddits.ProgressPics import ProgressPics
import pandas as pd

from Scrapper.Subreddits.util import Entry, save_image

p = Path.cwd() / 'dump'
pimg = (p / 'img')
p.mkdir(parents=True, exist_ok=True)
pimg.mkdir(parents=True, exist_ok=True)

subreddits = [Brogress(), ProgressPics()]
table = []
stats = {}


def write_table():
    with open(p / 'data.csv', 'a', newline='') as f:
        csv_out = csv.writer(f, delimiter=',')
        csv_out.writerows(table)


def delete(to_delete):
    csv_path = p / "data.csv"
    df = pd.read_csv(csv_path)
    for d in to_delete:
        os.remove(pimg / d)
        df = df[df.id != d.split(".jpg")[0]]
    df.to_csv(csv_path)


#
# with open(p / 'data.csv', 'w', newline='') as f:
#     csv_out = csv.writer(f, delimiter=',')
#     csv_out.writerow(Entry._fields)
#
# for idx, subreddit in enumerate(subreddits):
#     stats[subreddit.name] = {'correct': 0, 'error': 0}
#     for idx2, (entry, post) in enumerate(subreddit.process()):
#
#         if entry and save_image(post):
#             table.append(entry)
#             stats[subreddit.name]['correct'] = stats[subreddit.name]['correct'] + 1
#         else:
#             stats[subreddit.name]['error'] = stats[subreddit.name]['error'] + 1
#         if idx2 % 500 == 0 and idx2 != 0:
#             print(idx2)
#             write_table()
#             table = []
#
# write_table()

duplicates = []
hash_keys = {}

# print("Checking for duplicates")
# for index, filename in enumerate(os.listdir(pimg)):
#     if os.path.isfile(pimg / filename):
#         try:
#             with open(pimg / filename, 'rb') as f:
#                 if index % 1000 == 0:
#                     print(index)
#                 filehash = hashlib.md5(f.read()).hexdigest()
#
#                 if filehash not in hash_keys:
#                     hash_keys[filehash] = filename
#                 else:
#                     duplicates.append(filename)
#         except Exception as e:
#             print(e)
#             duplicates.append(filename)
#
# print("deleting duplicates")
# delete(duplicates)
# print(f"Deleted {len(duplicates)} duplicates")
# checking faces is done separate as it's way more expensive than calculating a hash
no_faces = []
faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

print("Checking faces")
for index, filename in enumerate(os.listdir(pimg)):
    fpath = pimg / filename
    if os.path.isfile(fpath):
        try:
            if index % 200 == 0:
                print(index)
            image = cv2.imread(fpath.as_posix(), 0)
            faces = faceCascade.detectMultiScale(
                image,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            if len(faces) == 0:
                no_faces.append(filename)
        except Exception as e:
            print(e)
            no_faces.append(filename)
delete(no_faces)

print(stats)
print(f'Found {len(duplicates)} duplicates')
print(f'Found {len(no_faces)} with no faces')
