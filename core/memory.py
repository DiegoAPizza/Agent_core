import redis
import json
from typing import List

class ContextWindow:
    def __init__(self, session_id: str, max_messages: int = 20, ttl: int = 3600):
        self.client = redis.Redis(host="localhost", port=6379, decode_responses=True)
        self.key = f"session:{session_id}:messages"
        self.max_messages = max_messages
        self.ttl = ttl  # segundos antes de expirar
    
    def add_message(self, role: str, content: str) -> None:
        # 1. Serializar el mensaje como JSON y agregarlo a la lista
        message = {"role": role, "content": content}
        message_json = json.dumps(message)
        self.client.rpush(self.key, message_json)
        self.client.ltrim(self.key, -self.max_messages, -1)
        self.client.expire(self.key, self.ttl)
        
    
    def get_messages(self) -> List[dict]:
        # Retornar todos los mensajes deserializados
        raw_messages=self.client.lrange(self.key,0,-1)
        
        return [json.loads(msg) for msg in raw_messages]
    
    def clear(self) -> None:
        # Eliminar la sesión
        self.client.delete(self.key)
        