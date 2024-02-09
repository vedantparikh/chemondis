import json
import os
from functools import wraps
from unittest.mock import MagicMock

import fakeredis
import redis
from django.conf import settings
from environs import Env

from api.singletonmeta import SingletonMeta


def ensure_serializable_key(func):
    """A decorator which ensure that redis keys can be properly serialized."""

    @wraps(func)
    def _check_key(_self, key, *args, **kwargs):
        """Check if the key is of a serializable type. """
        if not isinstance(key, str) and not isinstance(key, bytes):
            key = json.dumps(key)

        return func(_self, key, *args, **kwargs)

    return _check_key


class RedisClient(metaclass=SingletonMeta):
    """
    RedisClient to communicate with redis Server
    Redis Commands: https://redis.io/commands
    """

    class RedisContextManager:
        """A context manager for redis connection."""

        def __init__(self, connection_pool):
            self.connection_pool = connection_pool

        def __enter__(self):
            self.redis = redis.Redis(
                connection_pool=self.connection_pool)  # noqa pylint: disable=attribute-defined-outside-init
            try:
                self.redis.ping()
            except redis.ConnectionError:
                self.redis = None
            return self.redis

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_tb:
                print(f'Error in Redis connection: {exc_type} {exc_val} {exc_tb}')
            if self.redis is not None:
                self.redis.close()

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        # a global expiry time in seconds for all keys.
        self._env = Env()
        self.ex_seconds = self._env.int('REDIS_TTL_SECONDS', 60 * 60)
        self.ex_seconds_model = self._env.int('REDIS_TTL_MODEL_SECONDS', 60 * 60)
        self.connection_pool = redis.ConnectionPool(
            host=self.host,
            port=self.port,
            db=self.db,
            max_connections=1024,
            socket_timeout=5,
            health_check_interval=self.ex_seconds
        )

    def __repr__(self):
        return f'RedisClient(host={self.host}, port={self.port}, db={self.db})'

    @classmethod
    def make_from_env(cls):
        """Instantiate redis instance from env variables."""

        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = os.getenv('REDIS_PORT', 6379)
        redis_cache_db = os.getenv('REDIS_CACHE_DB', 0)

        return cls(host=redis_host, port=redis_port, db=redis_cache_db)

    def set(self, key, value, ex_seconds=None):
        """SET the string value of a key."""

        # use the expiry time if client passes it or set it to global expiry time
        ex_seconds = ex_seconds or self.ex_seconds
        key = json.dumps(key)
        with self.RedisContextManager(self.connection_pool) as client:
            if client is not None:
                result = client.set(key, json.dumps(value), ex=ex_seconds)
                print(f'Created new Redis cache with key: {key}.')

                return result

    def get(self, key):
        """GET the value of a key."""

        key = json.dumps(key)
        with self.RedisContextManager(self.connection_pool) as client:
            if client is not None:
                data = client.get(key)
                result = None
                if data:
                    print(f'Found Redis data for the given key: {key} from cache.')
                    result = json.loads(data)
                else:
                    print(f'Given key: {key} was not found.')
                return result

    def delete(self, key):
        """DELETE a key."""

        key = json.dumps(key)
        with self.RedisContextManager(self.connection_pool) as client:
            if client is not None:
                return client.delete(key)

    def exists(self, key):
        """To check the given key exists in Redis db."""

        key = json.dumps(key)
        with self.RedisContextManager(self.connection_pool) as client:
            if client is not None:
                return client.exists(key)

    def clear_on_pattern(self, pattern: str):
        """
        This Function matches the input search pattern and deletes that
        specific redis resource containing the given `pattern`.
        """

        count = 1
        pattern = f'*{pattern}*'
        with self.RedisContextManager(self.connection_pool) as client:
            if client is not None:
                for key in client.scan_iter(match=pattern, count=1):
                    client.unlink(key)
                    count += 1
                print(f'Cleared cache for {pattern}.')
                return count

    def flush_db(self):
        """Deletes all cache from current."""
        with self.RedisContextManager(self.connection_pool) as client:
            if client is not None:
                client.flushdb()

    def flush_all(self):
        """Deletes all cache."""
        with self.RedisContextManager(self.connection_pool) as client:
            if client is not None:
                client.flushall(asynchronous=True)

    # @ensure_connection
    def get_matching_keys(self, pattern: str):
        """Returns cache keys"""
        with self.RedisContextManager(self.connection_pool) as client:
            if client is not None:
                return client.keys(f'*{pattern}*')


class FakeRedisClient(metaclass=SingletonMeta):
    """Fake Redis Client for tests."""

    def __init__(self, connected=True):
        self.server = fakeredis.FakeServer()
        self.connected = connected
        self.client = None

        if connected:
            self.fake_redis()

    def fake_redis(self):
        """Fake Redis Client for tests."""
        self.server.connected = self.connected
        self.client = fakeredis.FakeRedis(server=self.server)
        return self.client

    @ensure_serializable_key
    def get(self, key):
        key = key.strip('"')
        data = self.client.get(key)
        res = None
        if data:
            res = json.loads(data)
        return res

    @ensure_serializable_key
    def set(self, key, value, ex_seconds=None):
        key = key.strip('"')
        if isinstance(value, MagicMock):
            return True
        return self.client.set(key, json.dumps(value))

    def clear_on_pattern(self, pattern: str):
        count = 1
        pattern = f'*{pattern}*'
        for key in self.client.scan_iter(match=pattern, count=1):
            self.client.unlink(key)
            count += 1
        return count

    def get_all_keys(self):
        key_list = self.client.keys('*')

        return [
            key.decode() for key in key_list
        ]

    @ensure_serializable_key
    def delete(self, key):
        return self.client.delete(key)

    def get_pattern_keys(self, pattern: str):
        pattern_key = f'*{pattern}*'
        key_list = self.client.keys(pattern_key)

        return [
            key.decode() for key in key_list
        ]

    def flush_all(self):
        """Deletes all cache."""

        self.client.flushall()

    def flush_db(self):
        """Deletes all cache from current."""

        self.client.flushdb()

    def exists(self, key):
        return self.client.exists(key)

    def get_matching_keys(self, pattern: str):
        return [json.dumps(key.decode()) for key in self.client.keys(f'*{pattern}*')]


def get_redis():
    """ get the redis client to use. """

    if settings.IS_TEST_ENV:
        return FakeRedisClient()

    return RedisClient.make_from_env()
