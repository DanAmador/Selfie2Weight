from mongoengine import *


class MetaData(Document):
    title = StringField(max_length=200, required=True)
    present = BooleanField(required=True, default=False)


class SanitizedEntry(Document):
    reddit_id = ObjectIdField(db_field="reddit_id", unique=True)
    id = ObjectIdField(db_field="reddit_id", unique=True)
    weight = DecimalField(min_value=0)
    local_path = StringField(required=True)
    height = DecimalField(min_value=0)
    width = DecimalField(min_value=0)
    x = DecimalField(min_value=0)
    y = DecimalField(min_value=0)
    feature_meta = EmbeddedDocumentListField(MetaData)


class RawEntry(Document):
    title = StringField(max_length=200, required=True)
    sex = StringField(max_length=200, required=True)
    age = IntField(required=True)
    height = DecimalField(min_value=0)
    start_weight = DecimalField(min_value=0)
    end_weight = DecimalField(min_value=0)
    reddit_id = ObjectIdField(db_field="reddit_id", unique=True)
    img_url = StringField(max_length=200, required=True)
    local_path = StringField(required=True)
    has_been_sanitized = BooleanField(required=True, default=False)
    sanitized_entries = ListField(ReferenceField(SanitizedEntry))

    raw_meta = EmbeddedDocumentListField(MetaData)
