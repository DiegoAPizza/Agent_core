from sentence_transformers import SentenceTransformer
from db.base import SessionLocal
from db.model import MemoryChunk
import uuid

model = SentenceTransformer("all-MiniLM-L6-v2")
class LongTermMemory:
    
    def store(self, session_id: str, content: str) -> None:
        embedding = model.encode(content).tolist()
        chunk = MemoryChunk(
        id=str(uuid.uuid4()),
        session_id=session_id,
        content=content,
        embedding=embedding
        )
        with SessionLocal() as db:
            db.add(chunk)
            db.commit()
    
    def retrieve(self, query: str, top_k: int = 3) -> list[str]:
        # 1. Generar embedding de la query
        query_embedding = model.encode(query).tolist()
        # 2. Buscar los top_k chunks más similares en PGVector
        # 3. Retornar lista de strings con el content
        with SessionLocal() as db:
            results = (
                db.query(MemoryChunk)
                .order_by(MemoryChunk.embedding.cosine_distance(query_embedding))
                .limit(top_k)
                .all()
            )
        return [chunk.content for chunk in results]