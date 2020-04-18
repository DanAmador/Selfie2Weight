import csv
from pathlib import Path

from Scrapper.Subreddits.AbstractSubreddit import Entry
from Scrapper.Subreddits.Brogress import Brogress
from Scrapper.Subreddits.ProgressPics import ProgressPics
from Scrapper.Subreddits.util import save_image

p = Path.cwd() / 'dump'
pimg = (p / 'img')
p.mkdir(parents=True, exist_ok=True)
pimg.mkdir(parents=True, exist_ok=True)

subreddits = [Brogress(), ProgressPics()]
table = []
stats = {}
for idx, subreddit in enumerate(subreddits):
    for idx2, (entry, post) in enumerate(subreddit.process()):
        if idx2 % 500 == 0:
            print(idx2)
        if entry and save_image(post):
            table.append(entry)
        else:
            s = stats.get(idx, {'error': 0})
            s['error'] += 1

for idx, s in enumerate(subreddits):
    print("%s: ".format(s.name) + stats[idx])

with open(p / 'data.csv', 'w') as out:
    csv_out = csv.writer(out)
    csv_out.writerow(list(Entry._fields))
    csv_out.writerows(table)
