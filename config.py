import os
import redis

# Переменные окружения
host_redis = os.getenv("redis")

# Инициализация Redis-клиента
redis_client = redis.Redis(host="redis", port=6379, db=0)
