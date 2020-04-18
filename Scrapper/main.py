import csv
import urllib
from collections import namedtuple
import praw
from psaw import PushshiftAPI
import re
from pathlib import Path

pound_list = ["lb", "lbs", "pounds", "pound"]

Entry = namedtuple("Entry", "sex age height start_weight end_weight id")

# Gets values in the format of 5' 6"
inches_regex = re.compile("(\d+)['+ | ’] *(\d+)(?:\"|'')?")


def str2meter(height_str):
    m = re.match(r'(\d*)[c+]m', height_str)
    if m:
        m = float(m[1])
        return round(m if m < 3 else m / 100, 2), True

    match = inches_regex.match(height_str)
    if match:
        m = round(float(match[1]) * 0.3048 + float(match[2]) * 0.0254, 2)
        return m, True
    return 0, False


def get_bracket_weights(bracket_str):
    numbers = re.findall(r'(\d+(?:\.\d+)?)', bracket_string)

    if len(numbers) > 3:  # Sometimes people add conversions
        numbers = re.findall(r'(\d+(?:\.\d+)?)lb[s]*', bracket_string)

    if any([pound in bracket_str for pound in pound_list]):
        numbers = [round(float(num) * 0.453592, 2) for num in numbers]  # I want kg
    else:
        numbers = [float(num) for num in numbers]

    return numbers[:2], len(numbers) >= 2


# It creates 2 groups (Sex, Age, Height) and everything inside the brackets []
group_regex = re.compile("((F|M)\/(\d+)\/([^\[]*|[^\s]+))\[([^\]]*)")


# api = PushshiftAPI()

# gen = api.search_submissions(subreddit="progresspics")

gen = reddit.subreddit("progresspics").hot(limit=5)

p = Path.cwd() / 'dump'
pimg = (p / 'img')
p.mkdir(parents=True, exist_ok=True)
pimg.mkdir(parents=True, exist_ok=True)

table = []
for el in gen:
    match = group_regex.match(el.title)
    if match:
        height, height_parse_status = str2meter(match[4])
        bracket_string = match.group(5)
        weights, bracket_status = get_bracket_weights(bracket_string)
        # , "age sex height start_weight end_weight id")
        if bracket_status and el.url.endswith(".jpg") and height_parse_status:
            table.append(Entry(match[2], match[3], height, max(weights), min(weights), el.id))
            print(table)
            print(el.url)
        try:
            response = urllib.request.urlopen(el.url)
        except:
            break
        img = response.read()

        name = str(el.id) + '.jpg'
        pimg.touch(name)
        with open(pimg / name, 'wb') as f:
            f.write(img)

with open(p / 'data.csv','w') as out:
    csv_out=csv.writer(out)
    csv_out.writerow(list(Entry._fields))
    csv_out.writerows(table)

# for val in next(gen):
#     print(val)
# #
# print(reddit.read_only)
#
# for submission in reddit.subreddit('progresspics').hot(limit=10):
#     print(submission)
