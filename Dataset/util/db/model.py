from dataclasses import dataclass
from mongoengine import *


@dataclass
class Bbox:
    x1: float
    y1: float
    x2: float
    y2: float

    def contains(self, other: "Bbox"):
        return self.x1 < other.x1 or self.y1 < other.y1 or self.x2 > other.x2 or self.y2 > other.x2

    def to_tuple(self):
        return self.x1, self.y1, self.x2, self.y2


class FeatureMeta(EmbeddedDocument):
    x = IntField(required=True)
    y = IntField(required=True)
    width = IntField(required=True)
    height = IntField(required=True)

    @property
    def bounding_box(self):
        return Bbox(self.x, self.y, self.x + self.width, self.y + self.height)


class RawEntry(Document):
    title = StringField(required=True)
    reddit_id = StringField(unique=True)
    weight = DecimalField(min_value=0)
    sex = StringField(required=True)
    age = IntField(required=True, min_value=10, max_value=100)
    height = DecimalField(min_value=0, max_value=2.2)
    start_weight = DecimalField(min_value=0)
    end_weight = DecimalField(min_value=0)
    img_url = StringField(max_length=200, required=True)
    local_path = StringField()
    sanitized_entries = ListField(ReferenceField("SanitizedEntry"))
    raw_meta = DictField(EmbeddedDocumentListField(FeatureMeta))
    has_been_sanitized = BooleanField(required=True, default=False)
    was_preprocessed = BooleanField(required=True, default=False)
    has_image = BooleanField(required=True, default=False)
    sanitized_by = StringField()


class SanitizedEntry(Document):
    reddit_id = StringField()
    weight = DecimalField(min_value=0)
    height = DecimalField(min_value=0)
    width = DecimalField(min_value=0)
    x = DecimalField(min_value=0)
    y = DecimalField(min_value=0)
    age = IntField(required=True)

    @property
    def bounding_box(self):
        return Bbox(self.x, self.y, self.x + self.width, self.y + self.height)
