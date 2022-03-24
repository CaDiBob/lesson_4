import redis
from environs import Env


def get_connect_db():
    env = Env()
    env.read_env()
    db = redis.Redis(
        host=env('REDIS_HOST'),
        port=env('REDIS_PORT'),
        password=env('REDIS_PASSWORD'),
        decode_responses=True,
    )
    return db
