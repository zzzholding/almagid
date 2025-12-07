import redis
import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "alma_redis"),
    port=6379,
    db=0,
    decode_responses=True
)
