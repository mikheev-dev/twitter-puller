import json
import os
import sys

sys.path.insert(1, os.path.abspath(".."))

from lib.connectors.psql_connection import get_psql_connection
from lib.config import BaseConfig, DevConfig

PATH_TO_ACCOUNTS = 'test_accounts.json'


def create_database(config: BaseConfig):
    connection = get_psql_connection(config, dbname='bigten')
    cursor = connection.cursor()
    cursor.execute(
        """
            SELECT datname FROM pg_catalog.pg_database WHERE datname = 'twitter';
        """
    )
    result = cursor.fetchall()
    if not result:
        cursor.execute("""CREATE DATABASE twitter;""")
    connection.close()


def create_accounts_table(cursor):
    query = """
        CREATE TABLE IF NOT EXISTS accounts (
           id BIGINT PRIMARY KEY NOT NULL ,
           name VARCHAR (50) NOT NULL ,
           tags VARCHAR (50) [] DEFAULT '{}' NOT NULL,
           description TEXT NOT NULL 
        );
    """
    cursor.execute(query)


def create_tables(connection):
    with connection:
        with connection.cursor() as cursor:
            print('Create account table')
            create_accounts_table(cursor)
            print('Create tweets table')
            create_tweets_table(cursor)


def fill_accounts_values(connection, path_to_file: str):
    with open(path_to_file) as f:
        accounts = json.load(f)
    with connection:
        with connection.cursor() as cursor:
            for account in accounts:
                cursor.execute(
                    f"""
                        INSERT INTO accounts (id, name, tags, description)
                        VALUES (%s, %s, %s, %s);
                    """,
                    (
                        account['id'],
                        account['name'],
                        account['tags'],
                        account['desc']
                    )
                )


def create_tweets_table(cursor):
    query = """
        CREATE TABLE IF NOT EXISTS tweets (
           id BIGINT PRIMARY KEY NOT NULL,
           user_id BIGINT NOT NULL,
           created_at TIMESTAMP NOT NULL DEFAULT NOW(),
           txt TEXT NOT NULL DEFAULT '',
           tags VARCHAR (50) [] DEFAULT '{}' NOT NULL,
           is_retweet BOOLEAN NOT NULL DEFAULT FALSE,
           media VARCHAR (300) [] DEFAULT '{}' NOT NULL,
           doc jsonb NOT NULL
        );
    """
    cursor.execute(query)


if __name__ == "__main__":
    cfg = DevConfig()
    print('Create database')
    create_database(cfg)
    connection = get_psql_connection(cfg, dbname='twitter')
    print('Create tables')
    create_tables(connection)
    print('Fill accounts')
    fill_accounts_values(connection, path_to_file=PATH_TO_ACCOUNTS)
    connection.close()
