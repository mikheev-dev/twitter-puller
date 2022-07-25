from logging import Logger
from multiprocessing import Queue, get_logger

import logging

from lib.mp.controller import MPController
from lib.mp.publisher import MPQueuePublisher
from lib.mp.receiver import MPQueueReceiver
from lib.mp.wrapper import MPWrapper

from db_twitter_writer.writer import DBTwitterWriter
from db_twitter_writer.db_twitter_publisher import BasePostgresTwitterPublisher
from tags_extractor.extractor import TagsExtractorService
from twitter_listener.listener import TwitterListener
from lib.service.service import PipelineService


def get_mp_logger(log_level) -> Logger:
    level = log_level
    logger = get_logger()
    formatter = logging.Formatter("%(asctime)s]:[%(name)s]:{%(levelname)s}:%(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


class TwitterPoolerService(MPController):
    def __init__(
            self,
            listener: TwitterListener,
            tags_extractor: TagsExtractorService,
            writer: DBTwitterWriter,
            logger: Logger,
    ):
        super(TwitterPoolerService, self).__init__()
        self._logger = logger
        self._processes = {
            'listener': MPWrapper(listener),
            'writer': MPWrapper(writer),
            'tag_extractor': MPWrapper(tags_extractor),
        }


mp_logger = get_mp_logger(log_level='DEBUG')


if __name__ == "__main__":
    unparsed_q = Queue()
    parsed_q = Queue()
    listener = TwitterListener(
        publisher=MPQueuePublisher(queue=unparsed_q),
        logger=mp_logger,
    )

    tags_extractor = TagsExtractorService(
        receiver=MPQueueReceiver(queue=unparsed_q),
        publisher=MPQueuePublisher(queue=parsed_q),
        logger=mp_logger,
    )

    writer = DBTwitterWriter(
        receiver=MPQueueReceiver(queue=parsed_q),
        db_publisher=BasePostgresTwitterPublisher(),
        logger=mp_logger,
    )

    controller = TwitterPoolerService(
        listener=listener,
        tags_extractor=tags_extractor,
        writer=writer,
        logger=mp_logger
    )
    controller.run()
