import redis
from app.config import settings

# Connect to Redis
redis_client = redis.Redis(
    host=settings.redis_host, 
    port=settings.redis_port, 
    decode_responses=True
)

def get_chat_history(session_id: str, limit: int = 6) -> str:
    """Fetches the last few messages for this session from Redis."""
    key = f"chat_history:{session_id}"
    
    # Grab the last N messages (limit * 2 because of User + AI pairs)
    messages = redis_client.lrange(key, -limit * 2, -1)
    
    if not messages:
        return "No previous conversation history."
        
    return "\n".join(messages)

def save_to_history(session_id: str, user_query: str, ai_response: str):
    """Saves the newest back-and-forth to Redis."""
    key = f"chat_history:{session_id}"
    
    # Add the new messages to the end of the list
    redis_client.rpush(key, f"Human: {user_query}")
    redis_client.rpush(key, f"AI: {ai_response}")
    
    # Set a 2-hour expiration timer so abandoned chats don't eat up server RAM!
    redis_client.expire(key, 7200)
