"""Definitions of all api calls."""
import json
from typing import Optional

from ..http_request.http_method import HttpMethod
from ..http_request.request_details import RequestDetails
from ..model.cursor import Cursor

_default_tweets_count_in_batch = 20


class TwitterApiRequests:
    """Definitions of all api calls."""

    timeout: int

    def __init__(self, timeout: int = 60):
        """Constructor TwitterApiRequests."""
        self.timeout = timeout

    def get_guest_token_request_details(self):
        """Method return request details to get guest token."""
        return RequestDetails(
            HttpMethod.POST,
            'https://api.twitter.com/1.1/guest/activate.json',
            dict(),
            dict(),
            self.timeout
        )

    def get_search_tweet_request_details_new_api(
            self,
            all_download_tweets_count: int,
            cursor: Cursor,
            tweets_limit: Optional[int],
            full_search_query: str
    ) -> RequestDetails:
        count = _default_tweets_count_in_batch \
            if tweets_limit is None \
            else min(_default_tweets_count_in_batch, tweets_limit - all_download_tweets_count)
        params = dict([
            ('include_profile_interstitial_type', '1'),
            ('include_blocking', '1'),
            ('include_blocked_by', '1'),
            ('include_followed_by', '1'),
            ('include_want_retweets', '1'),
            ('include_mute_edge', '1'),
            ('include_can_dm', '1'),
            ('include_can_media_tag', '1'),
            ('skip_status', '1'),
            ('cards_platform', 'Web-12'),
            ('include_cards', '1'),
            ('include_ext_alt_text', 'true'),
            ('include_quote_count', 'true'),
            ('include_reply_count', '1'),
            ('tweet_mode', 'extended'),
            ('include_entities', 'true'),
            ('include_user_entities', 'true'),
            ('include_ext_media_color', 'true'),
            ('include_ext_media_availability', 'true'),
            ('send_error_codes', 'true'),
            ('simple_quoted_tweet', 'true'),
            ('q', full_search_query),
            ('count', count),
            ('query_source', 'typed_query'),
            ('pc', '1'),
            ('spelling_corrections', '1'),
            ('ext', 'mediaStats,highlightedLabel,voiceInfo')
        ])
        if cursor is not None:
            params['cursor'] = cursor.value
        return RequestDetails(
            HttpMethod.GET,
            url='https://twitter.com/i/api/2/search/adaptive.json',
            headers=dict(),
            params=params,
            timeout=self.timeout
        )

    def get_user_details_request_details(self, user_screen_name: str) -> RequestDetails:
        variable_query = {
            "screen_name": user_screen_name,
            "withSafetyModeUserFields": True,
            "withSuperFollowsUserFields": True
        }
        _graphql_token = 'cYsDlVss-qimNYmNlb6inw'  # token generated for ony request in browser
        return RequestDetails(
            http_method=HttpMethod.GET,
            url=f'https://twitter.com/i/api/graphql/{_graphql_token}/UserByScreenName',
            headers=dict(),
            params=dict({
                'variables': json.dumps(variable_query)
            }),
            timeout=self.timeout
        )

    def get_tweet_request_by_id(self, tweet_id: str, cursor: Optional[Cursor]) -> RequestDetails:
        variable_query = {
            "focalTweetId": tweet_id,
            "with_rux_injections": True,
            "includePromotedContent": True,
            "withCommunity": True,
            "withTweetQuoteCount": True,
            "withBirdwatchNotes": True,
            "withSuperFollowsUserFields": True,
            "withUserResults": True,
            "withBirdwatchPivots": True,
            "withReactionsMetadata": True,
            "withReactionsPerspective": True,
            "withSuperFollowsTweetFields": True,
            "withVoice": True
        }
        if cursor is not None:
            variable_query['cursor'] = cursor.value
        _graphql_token = 'kUnCMgMYZCR8GyRZz76IQg'
        return RequestDetails(
            http_method=HttpMethod.GET,
            url=f'https://twitter.com/i/api/graphql/{_graphql_token}/TweetDetail',
            headers=dict(),
            params=dict({
                'variables': json.dumps(variable_query)
            }),
            timeout=self.timeout
        )

    def get_tweet_request_by_user(self, user_id: str, cursor: Optional[Cursor]) -> RequestDetails:
        variable_query = {
            "userId": user_id,
            "count": 40,
            "includePromotedContent": True,
            "withQuickPromoteEligibilityTweetFields": True,
            "withDownvotePerspective": False,
            "withVoice": True,
            "withV2Timeline": True,
        }
        feature_query = {
            "blue_business_profile_image_shape_enabled": False,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "tweetypie_unmention_optimization_enabled": True,
            "vibe_api_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": False,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": False,
            "interactive_text_enabled": True,
            "responsive_web_text_conversations_enabled": False,
            "longform_notetweets_rich_text_read_enabled": False,
            "responsive_web_enhance_cards_enabled": False
        }
        if cursor is not None:
            variable_query['cursor'] = cursor.value
        _graphql_token = 'QlY1BVw8TLG6qrIAEhVMiw'
        return RequestDetails(
            http_method=HttpMethod.GET,
            url=f'https://twitter.com/i/api/graphql/{_graphql_token}/UserTweets',
            headers=dict(),
            params=dict({
                'variables': json.dumps(variable_query),
                'features': json.dumps(feature_query)
            }),
            timeout=self.timeout
        )
