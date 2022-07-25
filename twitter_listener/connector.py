from logging import Logger, getLogger
from typing import List, Optional, Dict
from tweepy.tweet import Tweet

import datetime
import pytz
import time
import tweepy

from lib.connectors.psql_connection import get_psql_connection
from lib.event import Event
from lib.pubsub.publisher import BasePublisher
from lib.service.service import BaseService
from lib.pubsub.mixin import PublisherMixin
from twitter_listener.config import TwitterConnectorConfig
from twitter_listener.tweet_serializer import TweetSerializer

config = TwitterConnectorConfig()
default_logger = getLogger('TweeterAccountConnector')


class TweeterAccountConnector(PublisherMixin, BaseService):
    _followed_account_id: int
    _followed_account: str
    _client: tweepy.Client
    _last_timestamp: datetime.datetime

    def __init__(
            self,
            account_id: int,
            account_name: str,
            publisher: BasePublisher,
            logger: Logger = default_logger,
    ):
        super().__init__()
        self._logger = logger
        self.set_publisher(publisher)
        self._followed_account_id = account_id
        self._followed_account = account_name
        self._client = tweepy.Client(bearer_token=config.BEARER_TOKEN)

    def _get_tweets(self, start_time: Optional[datetime.datetime] = None) -> tweepy.Response:
        args = {
            'query': f'from:{self._followed_account}',
            'tweet_fields': ['created_at', 'entities', 'author_id'],
            'expansions':  ['referenced_tweets.id', 'attachments.media_keys'],
            'media_fields': ['media_key', 'type', 'url', 'preview_image_url'],
            'max_results': 100,
        }
        if start_time:
            args.update({
                'start_time': start_time
            })
        response = self._client.search_recent_tweets(**args)
        return response

    def receive(self) -> List[Dict]:
        time.sleep(config.POOL_TIME)
        start_time = datetime.datetime.now(tz=datetime.timezone.utc)
        response = self._get_tweets(start_time=self._last_timestamp.replace(tzinfo=pytz.utc))
        tweets = TweetSerializer.serialize(response)
        self._logger.debug(f"{self._service_name}::{self._followed_account}::"
                           f"Success read tweets for account {self._followed_account}!")
        self._last_timestamp = start_time
        return tweets

    def _prepare_db_connection(self):
        self._connection = get_psql_connection(cfg=config, dbname='twitter')

    def get_tweets_for_default_pooling_period(self) -> datetime.datetime:
        self._logger.debug(f"{self._service_name}::{self._followed_account}::Start to read tweets for a week!")
        response = self._get_tweets()
        self._logger.debug(f"{self._service_name}::{self._followed_account}::Successful readed tweets for a week!")
        created_at = response.data[0].created_at
        tweets = TweetSerializer.serialize(response)
        for tweet in tweets:
            self._publisher.publish(
                event=Event(
                    type='raw',
                    body=tweet,
                )
            )
        return created_at + datetime.timedelta(seconds=1) if response.data else datetime.datetime.now(tz=datetime.timezone.utc)

    def prepare_initial_date(self):
        with self._connection:
            with self._connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT MAX(created_at) FROM tweets WHERE user_id=%s;
                    """,
                    (self._followed_account_id, )
                )
                last_timestamp = cursor.fetchone()
        if not last_timestamp[0]:
            self._logger.debug(f"{self._service_name}::{self._followed_account}::"
                               f"Empty tweets for account, read for a week!")
            self._last_timestamp = self.get_tweets_for_default_pooling_period()
        else:
            self._last_timestamp = last_timestamp[0]

    def setup(self):
        self._prepare_db_connection()
        self._logger.info(f"{self._service_name}::{self._followed_account}::Prepare initial data!")
        self.prepare_initial_date()
        self._logger.info(f"{self._service_name}::{self._followed_account}::"
                          f"Start reading tweets for account {self._followed_account}")

    def main(self):
        tweets: List[Dict] = self.receive()
        for tweet in tweets:
            self._publisher.publish(
                event=Event(
                    type='raw',
                    body=tweet,
                )
            )
