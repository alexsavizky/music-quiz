from dataclasses import dataclass
from typing import List


@dataclass
class Track:
    id: str
    name: str
    preview_url: str


@dataclass
class Artist:
    name: str
    genres: List[str]
    top_tracks: List[Track]
