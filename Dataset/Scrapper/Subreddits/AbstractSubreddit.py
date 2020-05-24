from abc import ABC, abstractmethod

from psaw import PushshiftAPI

from Dataset.util.db.model import RawEntry


class AbstractSubreddit(ABC):

    @abstractmethod
    def parse_post(self, post) -> RawEntry:
        pass

    def __init__(self) -> None:
        self.api = PushshiftAPI()
        self.name = "abstract"

    def process(self) :
        gen = self.api.search_submissions(subreddit=self.name)
        for el in gen:
            if not el.url:
                yield None
                continue
            yield self.parse_post(el), el
