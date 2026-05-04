# app/utils/cache.py
import redis
import hashlib
import json
from app.config import settings

# Initialize the Redis connection using our secure config
try:
    redis_client = redis.Redis(
        host=settings.redis_host, 
        port=settings.redis_port, 
        db=0, 
        decode_responses=True
    )
except Exception as e:
    print(f"Failed to connect to Redis: {e}")
    redis_client = None

def generate_cache_key(session_id: str, query: str) -> str:
    """
    Creates a unique, deterministic hash for a specific user's query.
    We hash it so long queries don't create massive Redis keys.
    """
    raw_key = f"{session_id}:{query.strip().lower()}"
    return hashlib.sha256(raw_key.encode()).hexdigest()

def get_cached_response(session_id: str, query: str):
    """Retrieves a cached response if it exists."""
    if not redis_client:
        return None
    
    key = generate_cache_key(session_id, query)
    cached_data = redis_client.get(key)
    
    if cached_data:
        return json.loads(cached_data)
    return None

def set_cached_response(session_id: str, query: str, response_data: dict, ttl_seconds: int = 3600):
    """Stores the response in Redis with a Time-To-Live (TTL) of 1 hour."""
    if not redis_client:
        return
        
    key = generate_cache_key(session_id, query)
    # Store the dictionary as a JSON string
    redis_client.setex(key, ttl_seconds, json.dumps(response_data))