import json
from typing import Any, Optional
from redis import Redis
from pydantic import BaseModel

class CacheService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.prefix = "clerk:user:"
        self.default_ttl = 3600  # 1 hour

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set a value in the cache with optional TTL"""
        full_key = f"{self.prefix}{key}"
        
        if isinstance(value, BaseModel):
            value = value.dict()
            
        try:
            serialized = json.dumps(value)
            if ttl is None:
                ttl = self.default_ttl
                
            return self.redis.setex(full_key, ttl, serialized)
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False

    def get(self, key: str) -> Optional[dict]:
        """Get a value from the cache"""
        full_key = f"{self.prefix}{key}"
        
        try:
            data = self.redis.get(full_key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Error getting from cache: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete a value from the cache"""
        full_key = f"{self.prefix}{key}"
        
        try:
            return bool(self.redis.delete(full_key))
        except Exception as e:
            print(f"Error deleting from cache: {e}")
            return False

    def user_cache(self, clerk_id: str, user_data: Any) -> bool:
        """Cache user data by clerk ID"""
        return self.set(clerk_id, user_data)