from logging import Logger

from db_twitter_writer.db_twitter_publisher import BasePostgresPublisher
from lib.service.service import PipelineService
from lib.pubsub.receiver import BaseReceiver


class DBTwitterWriter(PipelineService):
    def __init__(
            self,
            receiver: BaseReceiver,
            db_publisher: BasePostgresPublisher,
            logger: Logger
     ):
        super().__init__(
            receiver=receiver,
            publisher=db_publisher,
            logger=logger,
        )
