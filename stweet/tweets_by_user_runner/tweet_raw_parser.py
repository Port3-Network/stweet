import json
from typing import List, Union

import arrow

from ..model.cursor import Cursor
from ..model.user_tweet_raw import UserTweetRaw


def _parse_tweets_entry_content(entry_content) -> Union[None, Cursor, UserTweetRaw]:
    entry_type = entry_content['entryType']
    if entry_type == 'TimelineTimelineCursor':
        return Cursor(entry_content['cursorType'], entry_content['value'])

    if entry_type == 'TimelineTimelineItem':
        item_content = entry_content['itemContent']
        item_content_type = item_content['itemType']
        if item_content_type == 'TimelineTweet':
            return UserTweetRaw(json.dumps(item_content['tweet_results']['result']), arrow.now())
    elif entry_type == 'TimelineTimelineModule':
        item = entry_content['items'][0]
        if item['item']['itemContent']['itemType'] == 'TimelineTweet':
            return UserTweetRaw(json.dumps(item['item']['itemContent']['tweet_results']['result']),
                                arrow.now())
    else:
        return None


def get_all_tweets_from_json(json_str: str) -> List[Union[UserTweetRaw, Cursor]]:
    response_obj = json.loads(json_str)
    instructions = response_obj['data']['user']['result']['timeline_v2']['timeline']['instructions']
    tweet_instruction = [it for it in instructions if it['type'] == 'TimelineAddEntries'][0]
    entries = tweet_instruction['entries']
    to_return = [_parse_tweets_entry_content(it['content']) for it in entries]
    return [it for it in to_return if it is not None]
