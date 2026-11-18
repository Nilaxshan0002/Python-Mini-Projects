import redis
import os
import json
from dotenv import load_dotenv

load_dotenv()
redis_client = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)

def set_latest_status(endpoint_id: int, data: dict):
    redis_client.set(f"endpoint:{endpoint_id}", json.dumps(data), ex=300) # Expire in 5 mins

def get_latest_status(endpoint_id: int):
    data = redis_client.get(f"endpoint:{endpoint_id}")
    return json.loads(data) if data else None