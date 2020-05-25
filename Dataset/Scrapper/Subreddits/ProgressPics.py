from Scrapper.Subreddits.AbstractSubreddit import AbstractSubreddit
import re

from util.db.model import RawEntry


class ProgressPics(AbstractSubreddit):

    def __init__(self) -> None:
        super().__init__()
        self.name = "progresspics"
        # It creates 2 groups (Sex, Age, Height) and everything inside the brackets []
        self.group_regex = re.compile("((F|M)\/(\d+)\/([^\[]*|[^\s]+))\[([^\]]*)")
        # Gets values in the format of 5' 6"
        self.inches_regex = re.compile("(\d+)['+ | ’] *(\d+)(?:\"|'')?")
        self.pound_list = ["lb", "lbs", "pounds", "pound"]

    def parse_post(self, post) -> RawEntry:
        match = self.group_regex.match(post.title)
        if match:
            height, height_parse_status = self.str2meter(match[4])
            bracket_string = match.group(5)
            weights, bracket_status = self.get_bracket_weights(bracket_string)
            # , "age sex height start_weight end_weight id")
            if bracket_status and post.url.endswith(".jpg") and height_parse_status:
                return RawEntry(title=post.title, sex=match[2], age=int(match[3]), height=height,
                                start_weight=max(weights),
                                end_weight=min(weights), reddit_id=post.id, img_url=post.url)

            return None

    def str2meter(self, height_str):
        m = re.match(r'(\d*)[c+]m', height_str)
        if m:
            m = float(m[1])
            return round(m if m < 3 else m / 100, 2), True

        match = self.inches_regex.match(height_str)
        if match:
            m = round(float(match[1]) * 0.3048 + float(match[2]) * 0.0254, 2)
            return m, True
        return 0, False

    def get_bracket_weights(self, bracket_str):
        numbers = re.findall(r'(\d+(?:\.\d+)?)', bracket_str)

        if len(numbers) > 3:  # Sometimes people add conversions
            numbers = re.findall(r'(\d+(?:\.\d+)?)lb[s]*', bracket_str)

        if any([pound in bracket_str for pound in self.pound_list]):
            numbers = [round(float(num) * 0.453592, 2) for num in numbers]  # I want kg
        else:
            numbers = [float(num) for num in numbers]

        return numbers[:2], len(numbers) >= 2
