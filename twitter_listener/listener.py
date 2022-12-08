import datetime
from dataclasses import dataclass
from logging import Logger, getLogger
from typing import List, Tuple

from lib.connectors.psql_connection import get_psql_connection
from lib.mp.controller import MPController
from lib.mp.wrapper import MPWrapper
from lib.pubsub.publisher import BasePublisher
from twitter_listener.config import TwitterConnectorConfig
from twitter_listener.connector import TweeterAccountConnector


default_logger = getLogger('TwitterPooler')
config = TwitterConnectorConfig()


@dataclass
class FollowingAccount:
    id: int
    name: str
    tags: List[str]
    last_update: datetime.datetime = None
    initial_wait_time: float = None


class TwitterListener(MPController):
    _accounts: List[FollowingAccount]
    _publisher: BasePublisher

    def __init__(self, publisher: BasePublisher, logger: Logger = default_logger):
        super().__init__()
        self._logger = logger
        self._accounts = []
        self._publisher = publisher

    def setup(self):
        self._accounts = self.setup_following_accounts()
        self._processes = {
            account.name: MPWrapper(
                service=TweeterAccountConnector(
                    account_id=account.id,
                    account_name=account.name,
                    publisher=self._publisher,
                    logger=self._logger,
                    account_tags=account.tags,
                    last_update=account.last_update,
                    initial_waiting_time=account.initial_wait_time
                )
            )
            for account in self._accounts
        }
        super().setup()

    def _get_accounts_from_db(self, connection) -> List[FollowingAccount]:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT id, name, tags FROM accounts;
                """
            )
            return [
                FollowingAccount(
                    id=account[0],
                    name=account[1],
                    tags=account[2]
                )
                for account in cursor.fetchall()
            ]

    def _set_last_update_for_accounts(
            self,
            accounts: List[FollowingAccount],
            connection
    ) -> None:
        for account in accounts:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT MAX(created_at) FROM tweets WHERE user_id=%s;
                    """,
                    (account.id, )
                )
                last_timestamp = cursor.fetchone()
            if last_timestamp[0]:
                account.last_update = last_timestamp[0]

    def _set_initial_waiting_times(self, accounts: List[FollowingAccount]) -> None:
        slot_duration = config.POOL_TIME // (len(accounts) // config.ACCOUNTS_IN_TIME_SLOT + 1)
        last_slot_start = 0
        last_account_batch = 0
        for idx, account in enumerate(accounts):
            account.initial_wait_time = last_slot_start
            if idx // config.ACCOUNTS_IN_TIME_SLOT > last_account_batch:
                last_account_batch += 1
                last_slot_start += slot_duration

    def setup_following_accounts(self) -> List[FollowingAccount]:
        cfg = TwitterConnectorConfig()
        connection = get_psql_connection(cfg, dbname=cfg.PSQL_DB)
        with connection:
            accounts: List[FollowingAccount] = self._get_accounts_from_db(connection)
            self._set_last_update_for_accounts(
                accounts=accounts, connection=connection
            )
            self._set_initial_waiting_times(accounts)
        return accounts

