from Agent_core.db.base import Base, engine
from Agent_core.db.model import MemoryChunk  # importante: registra el modelo en Base.metadata
from sqlalchemy import text

# 1. Crear la extensión vectorial si no existe
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    conn.commit()
    print("✅ Extensión 'vector' verificada/creada")

# 2. Crear todas las tablas registradas en Base
Base.metadata.create_all(bind=engine)
print("✅ Tablas creadas correctamente")

# 3. Verificar que memory_chunks existe
with engine.connect() as conn:
    result = conn.execute(text("SELECT to_regclass('public.memory_chunks');"))
    exists = result.scalar()
    if exists:
        print("✅ La tabla 'memory_chunks' existe")
    else:
        print("❌ La tabla 'memory_chunks' NO se creó")