import logging
import time
import tweepy

import sys

from twitter_listener.connector import TweeterAccountConnector
from twitter_listener.listener import TwitterListener, FollowingAccount
from db_twitter_writer.writer import DBTwitterWriter
from tags_extractor.extractor import TagsExtractorService
from db_twitter_writer.db_twitter_publisher import BasePostgresTwitterPublisher

from lib.pubsub.publisher import SyncPublisher
from lib.pubsub.receiver import SyncReceiver

from lib.config import BaseConfig
from collections import deque
from typing import List


logger = logging.getLogger("sync_service")
cfg = BaseConfig()


def get_logger(log_level) -> logging.Logger:
    level = log_level
    logger = logging.getLogger()
    formatter = logging.Formatter("%(asctime)s]:[%(name)s]:{%(levelname)s}:%(message)s")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


if __name__ == "__main__":
    logger = get_logger(cfg.LOG_LEVEL)
    unparsed_q = deque()
    parsed_q = deque()

    sync_publisher = SyncPublisher(
        queue=unparsed_q,
        logger=logger,
    )

    accounts: List[FollowingAccount] = TwitterListener(
        publisher=None,
        logger=logger,
    ).setup_following_accounts()

    tags_extractor = TagsExtractorService(
        receiver=SyncReceiver(queue=unparsed_q, logger=logger),
        publisher=SyncPublisher(queue=parsed_q, logger=logger),
        logger=logger,
        sync=True,
    )
    writer = DBTwitterWriter(
        receiver=SyncReceiver(queue=parsed_q, logger=logger),
        db_publisher=BasePostgresTwitterPublisher(),
        logger=logger,
        sync=True,
    )

    total_read_tweets_count = 0
    for account in accounts:
        twitter_reader = TweeterAccountConnector(
            account_id=account.id,
            account_name=account.name,
            publisher=sync_publisher,
            logger=logger,
            account_tags=account.tags,
            last_update=account.last_update,
            initial_waiting_time=0,
            sync=True,
        )
        idx = 0
        for _ in range(3):
            try:
                read_tweets_count = twitter_reader.sync()
                total_read_tweets_count += read_tweets_count
                break
            except tweepy.errors.TooManyRequests as e:
                logger.error(f"Error {e} occured!")
                sync_publisher.clear()
                time.sleep(60)
                idx += 1

        if idx >= 3:
            logger.error("Can't get tweets for 3 retry!")

        tags_extractor.sync()
        writer.sync()
        time.sleep(0.6)
    logger.info(f"Total read tweets count = {total_read_tweets_count}")
