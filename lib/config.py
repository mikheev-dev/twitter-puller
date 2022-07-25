from typing import Any, Callable

import os


def get_env_var(
        name: str,
        default: Any = None,
        cast: Callable[[Any], Any] = lambda x: x,
) -> Any:
    env_var = os.environ.get(name, default)
    return cast(env_var)


class BaseConfig:
    HOST = get_env_var('HOST', default='[::]')
    PORT = get_env_var('PORT', cast=int, default=8881)
    LOG_LEVEL = get_env_var('LOG_LEVEL', default='INFO')
    LOG_NAME = get_env_var('LOG_NAME', default='Log')
    PSQL_HOST = get_env_var('PSQL_HOST', default='127.0.0.1')
    PSQL_PORT = get_env_var('PSQL_PORT', cast=int, default=5432)
    PSQL_USER = get_env_var('PSQL_USER', default='user')
    PSQL_PASSWORD = get_env_var('PSQL_PASSWORD', default='password')


class DevConfig(BaseConfig):
    PSQL_USER = 'bgt'
    PSQL_PASSWORD = 'bigten'


DEV_STAGE = 'dev'

