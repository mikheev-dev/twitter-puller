from lib.config import BaseConfig, get_env_var


class DBTwitterWriterConfig(BaseConfig):
    LOG_NAME = 'DB Twitter Writer'
    API_KEY = get_env_var('API_KEY', default='Bg3xHna75Uqy8u2RaZKFZXAwx')
    API_SECRET = get_env_var('API_SECRET', default='Ks2ovPp5KWWMiauXkT4mASBF25DQIn6EmPq9w7WRf3nw0atwnL')
    BEARER_TOKEN = get_env_var(
        'BEARER_TOKEN',
        default='AAAAAAAAAAAAAAAAAAAAAAoSdgEAAAAAq4yiAbKoYeZClaKlmtLxyQWlfhg%3Dm9OLDC7R9FqBgsSV4CnYaxa3trqIinDGbWncjskVJttT3PGvW6'
    )
    ACCESS_TOKEN = '1534658305389277184-WqSnElpx0EU4CTiOpWfIG7gIMguvAP'
    ACCESS_TOKEN_SECRET = '0S21zBaS8che4P7npUYSF6AKSvGvSsD9ZQfhae5SzdcW5'
    PSQL_HOST = get_env_var('PSQL_HOST', default='127.0.0.1')
    PSQL_PORT = get_env_var('PSQL_PORT', cast=int, default=5432)
    PSQL_USER = get_env_var('PSQL_USER', default='bgt')
    PSQL_PASSWORD = get_env_var('PSQL_PASSWORD', default='bigten')
