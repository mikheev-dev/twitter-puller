from logging import Logger, getLogger
from typing import List, Optional, Dict

import datetime
import pytz
import time
import tweepy

from lib.event import Event
from lib.pubsub.publisher import BasePublisher
from lib.service.service import BaseService
from lib.pubsub.mixin import PublisherMixin
from twitter_listener.config import TwitterConnectorConfig
from twitter_listener.tweet_serializer import TweetSerializer

config = TwitterConnectorConfig()
default_logger = getLogger('TweeterAccountConnector')


class TweeterAccountConnector(BaseService, PublisherMixin):
    _followed_account_id: int
    _followed_account: str
    _client: tweepy.Client
    _last_timestamp: datetime.datetime
    _followed_tags: List[str]
    _waiting_time: float

    def __init__(
            self,
            account_id: int,
            account_name: str,
            account_tags: List[str],
            last_update: datetime.datetime,
            initial_waiting_time: float,
            publisher: BasePublisher,
            logger: Logger = default_logger,
            sync: bool = False,
    ):
        BaseService.__init__(self, sync)
        self._logger = logger
        self.set_publisher(publisher)
        self._followed_account_id = account_id
        self._followed_account = account_name
        self._client = tweepy.Client(bearer_token=config.BEARER_TOKEN)
        self._followed_tags = account_tags
        self._waiting_time = initial_waiting_time
        max_twitter_period_for_request = datetime.datetime.now() - datetime.timedelta(weeks=1)
        self._last_timestamp = (
            last_update
            if last_update and last_update > max_twitter_period_for_request
            else max_twitter_period_for_request
        )
        self._sync = sync

    def _get_tweets(self, start_time: Optional[datetime.datetime] = None) -> tweepy.Paginator:
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
        response = tweepy.Paginator(
            self._client.search_recent_tweets,
            **args
        )
        return response

    def receive(self) -> List[Dict]:
        if not self._last_timestamp:
            self._logger.debug(f"{self._service_name}::{self._followed_account}::"
                               f"Empty tweets for account, read for a week!")
        start_time = datetime.datetime.now(tz=datetime.timezone.utc)
        responses: tweepy.Paginator = self._get_tweets(start_time=self._last_timestamp.replace(tzinfo=pytz.utc))
        tweets = TweetSerializer.serialize_paginator(responses, tags=self._followed_tags)
        self._logger.info(f"{self._service_name}::{self._followed_account}::"
                          f"Success read {len(tweets)} tweets for account {self._followed_account} "
                          f"for period from {self._last_timestamp} to {start_time}")
        self._last_timestamp = start_time
        return tweets

    def get_tweets_for_default_pooling_period(self) -> datetime.datetime:
        self._logger.debug(f"{self._service_name}::{self._followed_account}::Start to read tweets for a week!")
        response_pages: tweepy.Paginator = self._get_tweets()
        self._logger.debug(f"{self._service_name}::{self._followed_account}::Successful read tweets for a week!")
        if not response_pages:
            return datetime.datetime.now(tz=datetime.timezone.utc)
        tweets = TweetSerializer.serialize_paginator(response_pages=response_pages, tags=self._followed_tags)
        created_at = tweets[0]['created_at']
        for tweet in tweets:
            self._publisher.publish(
                event=Event(
                    type='raw',
                    body=tweet,
                )
            )
        return created_at + datetime.timedelta(seconds=1)

    def prepare_initial_date(self):
        if self._last_timestamp:
            return
        self._logger.debug(f"{self._service_name}::{self._followed_account}::"
                           f"Empty tweets for account, read for a week!")
        self._last_timestamp = self.get_tweets_for_default_pooling_period()

    def setup(self):
        self._logger.debug(f"{self._service_name}::{self._followed_account}::"
                           f"Waiting initial time {self._waiting_time}s!")
        time.sleep(self._waiting_time)
        self._logger.info(f"{self._service_name}::{self._followed_account}::Prepare initial data!")
        self.prepare_initial_date()
        self._logger.info(f"{self._service_name}::{self._followed_account}::"
                          f"Start reading tweets for account {self._followed_account}")

    @staticmethod
    def sleep():
        time.sleep(config.POOL_TIME)

    def main(self) -> int:
        if not self._sync:
            self.sleep()
        tweets: List[Dict] = self.receive()
        for tweet in tweets:
            self._publisher.publish(
                event=Event(
                    type='raw',
                    body=tweet,
                )
            )
        return len(tweets)

    def sync(self) -> int:
        return self.main()
