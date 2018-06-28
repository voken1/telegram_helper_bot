# coding:utf-8
from vn_data import conf
import redis
import json


class Cache:
    def __init__(self):
        self._redis_pool = redis.ConnectionPool(
            host=conf.redis_conf['host'],
            port=conf.redis_conf['port'],
            db=conf.redis_conf['db'],
            decode_responses=conf.redis_conf['decode_responses'],
        )
        self._redis = redis.Redis(connection_pool=self._redis_pool)

    def set(self, name, value):
        self._redis.set(name, json.dumps(value))

    def get(self, name, default=None):
        v = self._redis.get(name)
        if v:
            return json.loads(v)
        return default
