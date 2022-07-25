from dataclasses import dataclass
from typing import Dict, List, Union

import datetime


@dataclass
class FullParsedTweetBody:
    tweet_id: int
    user_id: int
    tags: List
    txt: str
    is_retweet: bool
    media: List[str]
    created_at: datetime.datetime


@dataclass
class Event:
    type: str
    body: Union[FullParsedTweetBody, Dict]

