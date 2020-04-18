from abc import ABC, abstractmethod
from typing import Tuple

from praw.models import Submission
from psaw import PushshiftAPI

from Scrapper.Subreddits.util import Entry


class AbstractSubreddit(ABC):

    @abstractmethod
    def parse_post(self, post) -> Entry:
        pass

    def __init__(self) -> None:
        self.api = PushshiftAPI()
        self.name = "abstract"

    def process(self) -> Tuple[Entry, Submission]:
        gen = self.api.search_submissions(subreddit=self.name)
        for el in gen:
            if not el.url:
                yield None
                continue
            yield self.parse_post(el), el
