import dataclasses
import json

from db_twitter_writer.config import DBTwitterWriterConfig
from lib.event import Event
from lib.pubsub.db_publisher import BasePostgresPublisher

config = DBTwitterWriterConfig()


class BasePostgresTwitterPublisher(BasePostgresPublisher):
    def __init__(self):
        super().__init__(cfg=config, db_name=config.PSQL_DB)

    def write_to_db(self, event: Event):
        with self._connection:
            with self._connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO tweets (id, user_id, txt, tags, created_at, is_retweet, media, doc)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                    """,
                    (
                        event.body.tweet_id,
                        event.body.user_id,
                        event.body.txt,
                        event.body.tags,
                        event.body.created_at,
                        event.body.is_retweet,
                        event.body.media,
                        json.dumps(event.body.doc),
                    )
                )
