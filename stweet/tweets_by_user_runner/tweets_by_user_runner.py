"""Runner for get tweets by user."""
import json
from typing import List, Optional

import arrow

from ..exceptions import ScrapBatchBadResponse
from ..http_request import RequestDetails, RequestResponse, WebClient
from ..model import UserTweetRaw
from ..model.cursor import Cursor
from ..raw_output.raw_data_output import RawDataOutput
from ..twitter_api.default_twitter_web_client_provider import \
    DefaultTwitterWebClientProvider
from ..twitter_api.twitter_api_requests import TwitterApiRequests
from .tweet_raw_parser import get_all_tweets_from_json
from .tweets_by_user_context import TweetsByUserContext
from .tweets_by_user_result import TweetsByUserResult
from .tweets_by_user_task import TweetsByUserTask

_NOT_FOUND_MESSAGE = '_Missing: No status found with that ID.'


class TweetsByUserRunner:
    tweets_by_user_context: TweetsByUserContext
    tweets_by_user_task: TweetsByUserTask
    raw_data_outputs: List[RawDataOutput]
    web_client: WebClient

    def __init__(
            self,
            tweets_by_user_task: TweetsByUserTask,
            raw_data_outputs: List[RawDataOutput],
            tweets_by_user_context: Optional[TweetsByUserContext] = None,
            web_client: Optional[WebClient] = None,
    ):
        self.tweets_by_user_context = TweetsByUserContext() if tweets_by_user_context is None \
            else tweets_by_user_context
        self.tweets_by_user_task = tweets_by_user_task
        self.raw_data_outputs = raw_data_outputs
        self.web_client = web_client if web_client is not None \
            else DefaultTwitterWebClientProvider.get_web_client()
        return

    def run(self) -> TweetsByUserResult:
        """Main search_runner method."""
        while not self._is_end_of_scrapping():
            self._execute_next_tweets_request()
        return TweetsByUserResult(self.tweets_by_user_context.all_download_tweets_count)

    def _is_end_of_scrapping(self) -> bool:
        ctx = self.tweets_by_user_context
        if ctx.stop:
            return True
        is_cursor = ctx.cursor is not None
        was_any_call = ctx.requests_count > 0
        return was_any_call and not is_cursor

    @staticmethod
    def response_with_not_found(request_response: RequestResponse) -> bool:
        parsed = json.loads(request_response.text)
        return 'data' not in parsed or 'user' not in parsed['data']

    def _execute_next_tweets_request(self):
        request_params = self._get_next_request_details()
        response = self.web_client.run_request(request_params)
        if response.is_success():
            if self.response_with_not_found(response):
                self.tweets_by_user_context.add_downloaded_tweets_count_in_request(0)
                self.tweets_by_user_context.cursor = None
            else:
                parsed_list = get_all_tweets_from_json(response.text)
                cursors = [it for it in parsed_list if isinstance(it, Cursor)]
                cursor = cursors[1] if len(cursors) >= 2 else None
                user_tweet_raw = self._filter_result([it for it in parsed_list if isinstance(it, UserTweetRaw)])
                self.tweets_by_user_context.add_downloaded_tweets_count_in_request(len(user_tweet_raw))
                self.tweets_by_user_context.cursor = cursor
                self._process_new_tweets_to_output(user_tweet_raw)
        else:
            raise ScrapBatchBadResponse(response)
        return

    def _filter_result(self, user_tweet_raw: List[UserTweetRaw]) -> List[UserTweetRaw]:
        ctx = self.tweets_by_user_context
        if len(user_tweet_raw) == 0:
            ctx.stop = True
            return user_tweet_raw
        if self.tweets_by_user_task.until:
            # todo : user binary search
            for idx, tweet_raw in enumerate(user_tweet_raw):
                tweet = json.loads(tweet_raw.raw_value)
                create_at = arrow.get(tweet['legacy']['created_at'], "ddd MMM DD HH:mm:ss Z YYYY")
                if create_at <= self.tweets_by_user_task.until:
                    ctx.stop = True
                    return user_tweet_raw[:idx]
        elif ctx.all_download_tweets_count + len(user_tweet_raw) >= self.tweets_by_user_task.tweets_limit:
            ctx.stop = True
            return user_tweet_raw[:self.tweets_by_user_task.tweets_limit - ctx.all_download_tweets_count]
        return user_tweet_raw

    def _process_new_tweets_to_output(self, raw_data_list: List[UserTweetRaw]):
        for raw_output in self.raw_data_outputs:
            raw_output.export_raw_data(raw_data_list)
        return

    def _get_next_request_details(self) -> RequestDetails:
        return TwitterApiRequests().get_tweet_request_by_user(
            self.tweets_by_user_task.user_id,
            self.tweets_by_user_context.cursor
        )
