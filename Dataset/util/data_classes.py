from dataclasses import dataclass


@dataclass
class RawEntry:
    sex: str
    age: int
    height: float
    start_weight: float
    end_weight: float
    reddit_id: str
    img_url: str
    local_url: str = None
    sanitized: bool = False

    def __repr__(self) -> str:
        return "raw_entry"


@dataclass
class SanitizedEntry:
    sex: str
    age: int
    height: float
    weight: float
    reddit_id: str
    local_path: str

    def __repr__(self) -> str:
        return "sanitized"

