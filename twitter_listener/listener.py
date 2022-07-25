from logging import Logger, getLogger
from typing import List, Tuple

from lib.connectors.psql_connection import get_psql_connection
from lib.mp.controller import MPController
from lib.mp.wrapper import MPWrapper
from lib.pubsub.publisher import BasePublisher
from twitter_listener.config import TwitterConnectorConfig
from twitter_listener.connector import TweeterAccountConnector


default_logger = getLogger('TwitterPooler')


class TwitterListener(MPController):
    _accounts: List[Tuple[int, str]]
    _publisher: BasePublisher

    def __init__(self, publisher: BasePublisher, logger: Logger = default_logger):
        super().__init__()
        self._logger = logger
        self._accounts = self.setup_following_accounts()
        self._publisher = publisher

    def setup(self):
        self._processes = {
            account_name: MPWrapper(
                service=TweeterAccountConnector(
                    account_id=account_id,
                    account_name=account_name,
                    publisher=self._publisher,
                    logger=self._logger,
                )
            )
            for account_id, account_name in self._accounts
        }

        super().setup()

    @staticmethod
    def setup_following_accounts() -> List[Tuple[int, str]]:
        connection = get_psql_connection(cfg=TwitterConnectorConfig(), dbname='twitter')
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT id, name FROM accounts;
                    """
                )
                accounts = [(account[0], account[1]) for account in cursor.fetchall()]
                return accounts
