"""Domain TweetsByUserTask class."""
from dataclasses import dataclass
from typing import Optional

from arrow import Arrow


@dataclass(frozen=True)
class TweetsByUserTask:
    """
        Domain TweetsByUserTask class.
        If the until parameter is set, the tweets_limit parameter is invalidated
    """

    user_id: str
    until: Optional[Arrow]
    tweets_limit: Optional[int]

    def __init__(
            self,
            user_id: str,
            until: Optional[Arrow] = None,
            tweets_limit: Optional[int] = 80
    ):
        """Class constructor."""
        object.__setattr__(self, 'user_id', user_id)
        object.__setattr__(self, 'until', until)
        object.__setattr__(self, 'tweets_limit', tweets_limit)
        return
