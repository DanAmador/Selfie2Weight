from dataclasses import dataclass
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Boolean
from sqlalchemy import Enum as EnumDB
from sqlalchemy.orm import relationship

from Dataset.util.db.base_class import Base


class RawEntry(Base):
    __tablename__ = 'raw_entry'
    sex = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    height = Column(Float, nullable=False)
    start_weight = Column(Float, nullable=False)
    end_weight = Column(Float, nullable=False)
    reddit_id = Column(String, primary_key=True)
    img_url = Column(String, nullable=False)
    local_url = Column(String, default=None)
    sanitized = Column(Boolean, default=False, nullable=False)
    sanitized_entries = relationship("SanitizedEntry")
    @property
    def tablename(self) -> str:
        return "raw_entry"


class SanitizedEntry(Base):
    __tablename__ = 'sanitized_entry'
    id = Column('id', Integer, primary_key=True)
    weight = Column(Float, nullable=False)
    reddit_id = Column(String, ForeignKey('raw_entry.reddit_id'), nullable=False)
    local_path = Column(String, nullable=False)
