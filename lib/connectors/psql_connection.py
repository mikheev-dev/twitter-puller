import psycopg2

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from typing import Optional

from lib.config import BaseConfig


def get_psql_connection(cfg: BaseConfig, dbname: Optional[str] = None):
    connection = psycopg2.connect(
        dbname=dbname,
        user=cfg.PSQL_USER,
        password=cfg.PSQL_PASSWORD,
        host=cfg.PSQL_HOST,
        port=cfg.PSQL_PORT,
    )
    connection.autocommit = True
    return connection

