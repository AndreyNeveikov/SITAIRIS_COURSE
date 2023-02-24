import redis

from innotter.settings import REDIS_HOST, REDIS_PORT


redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
