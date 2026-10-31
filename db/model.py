from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy import func
from pgvector.sqlalchemy import Vector
from db.base import Base
import uuid
class MemoryChunk(Base):
    __tablename__ = "memory_chunks"
 
    # models.py — agregar nullable=False y uuid automático
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False) 
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)
    created_at = Column(DateTime, default=func.now())