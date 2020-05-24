from mongoengine import *


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
    has_been_sanitized = BooleanField(required=True, default=False)
    sanitized_entries = ListField(ReferenceField("SanitizedEntry"))
    raw_meta = ListField(DictField())


class SanitizedEntry(Document):
    reddit_id = StringField(unique=True)
    weight = DecimalField(min_value=0)
    local_path = StringField(required=True)
    height = DecimalField(min_value=0)
    width = DecimalField(min_value=0)
    x = DecimalField(min_value=0)
    y = DecimalField(min_value=0)


class FeatureMeta(Document):
    title = StringField(max_length=200, required=True)
    present = BooleanField(required=True, default=False)
