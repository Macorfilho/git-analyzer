import os
import redis
from rq import Queue
from redis.exceptions import ConnectionError as RedisConnectionError

_connection = None
_queue = None

def get_redis_connection():
    """Lazy initialization of Redis connection"""
    global _connection
    if _connection is None:
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        try:
            _connection = redis.from_url(redis_url)
            # Test the connection
            _connection.ping()
        except RedisConnectionError as e:
            raise RedisConnectionError(f"Failed to connect to Redis at {redis_url}: {e}")
    return _connection

def get_queue():
    """Lazy initialization of RQ Queue"""
    global _queue
    if _queue is None:
        _queue = Queue(connection=get_redis_connection())
    return _queue
