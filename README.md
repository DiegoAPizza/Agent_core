# AgentCore 🤖

**AgentCore** es un agente de IA conversacional construido con **FastAPI**, **Ollama** y un bucle de razonamiento tipo *ReAct* (Thought → Action → Observation). Utiliza herramientas (calculadora, fecha, búsqueda) expuestas vía **MCP** (Model Context Protocol), mantiene contexto de sesión en **Redis** y memoria a largo plazo en **PostgreSQL + pgvector**.

---

## 📋 Características

- **Bucle de agente ReAct**: razona, elige herramientas y responde en múltiples pasos.
- **Herramientas (tools)**: calculadora, fecha actual y búsqueda simulada.
- **Ejecución segura**: validación de argumentos con Pydantic y permisos por scopes.
- **Contexto de sesión**: historial de conversación almacenado en Redis con TTL.
- **Memoria a largo plazo**: embeddings generados con `sentence-transformers` y almacenados en PostgreSQL con pgvector para recuperación semántica.
- **Servidor de herramientas independiente**: FastMCP expone las tools vía SSE.
- **API REST** documentada automáticamente con Swagger UI.
- **Logging estructurado** en consola y archivo.

---

## 🏗️ Arquitectura
┌─────────────┐ HTTP ┌──────────────┐
│ Cliente │ ◄────────────► │ FastAPI │
│ (Swagger) │ │ (main.py) │
└─────────────┘ └──────┬───────┘
│
▼
┌──────────────┐
│ Agent Loop │
│(agent_loop.py)│
└──────┬───────┘
│
┌────────────────────┼────────────────────┐
▼ ▼ ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Ollama │ │ Harness │ │ Memoria │
│ (llama3.2) │ │ (harness.py) │ │ (Redis + PG) │
└──────────────┘ └──────┬───────┘ └──────────────┘
│
▼
┌──────────────┐
│ MCP Client │
│ (mcp_client) │
└──────┬───────┘
│ SSE
▼
┌──────────────┐
│ Tools Server │
│ (FastMCP) │
└──────────────┘

---

## 🧰 Requisitos previos

- **Python 3.10 – 3.12** (recomendado 3.11 o 3.12; **evita 3.13+** por incompatibilidades con algunas librerías).
- **Docker Desktop** (Windows/macOS) o Docker Engine (Linux).
- **Ollama** instalado y corriendo localmente.
- **Redis** y **PostgreSQL con pgvector** (puedes levantarlos con Docker, ver abajo).

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd agentcore

2. Crear y activar entorno virtual
bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
3. Instalar dependencias
bash
pip install -r requirements.txt
Si usas CPU y quieres evitar descargar CUDA, instala primero PyTorch CPU:

bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
4. Levantar servicios con Docker
Crea un archivo docker-compose.yml en la raíz con:

yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: agentcore-postgres
    environment:
      POSTGRES_USER: agent
      POSTGRES_PASSWORD: agent123
      POSTGRES_DB: agentcore
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: agentcore-redis
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data
    restart: unless-stopped

volumes:
  pgdata:
  redisdata:
Luego ejecuta:

bash
docker compose up -d
Verifica que ambos contenedores estén corriendo:

bash
docker compose ps
5. Inicializar la base de datos
Crea un archivo init_db.py en la raíz (si no existe) con el siguiente contenido:

python
from db.base import Base, engine
from db.model import MemoryChunk
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    conn.commit()
    print("✅ Extensión 'vector' creada/verificada")

Base.metadata.create_all(bind=engine)
print("✅ Tablas creadas correctamente")

with engine.connect() as conn:
    result = conn.execute(text("SELECT to_regclass('public.memory_chunks');"))
    if result.scalar():
        print("✅ La tabla 'memory_chunks' existe")
    else:
        print("❌ La tabla 'memory_chunks' NO se creó")
Ejecútalo:

bash
python init_db.py
6. Iniciar Ollama y descargar el modelo
En una terminal aparte:

bash
ollama serve
Y en otra (o en la misma si usas ollama run):

bash
ollama pull llama3.2
7. Levantar el servidor de herramientas (FastMCP)
En una terminal nueva:

bash
python tools_server/server.py
Debería quedar escuchando en http://0.0.0.0:8001.

8. Iniciar la API FastAPI
En otra terminal (con el entorno virtual activado):

bash
uvicorn main:app --reload --port 8000
Abre tu navegador en http://127.0.0.1:8000/docs para ver la documentación interactiva.

🧪 Uso
Probar el agente con el script de ejemplo
El archivo main.py incluye un bloque if __name__ == "__main__": con varias pruebas. Ejecútalo con:

bash
python main.py
Esto mostrará por consola los pasos del agente (Thought, Action, Observation, Final Answer).

Llamar al endpoint
El endpoint expuesto es POST /agent/chat. Ejemplo con curl:

bash
curl -X POST "http://127.0.0.1:8000/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuánto es 25 * 4?", "session_id": "test-001"}'
Respuesta esperada (resumida):

json
{
  "final_answer": "El resultado de 25 * 4 es 100.",
  "steps": [...]
}
📁 Estructura del proyecto
text
agentcore/
├── alembic/               # Migraciones (opcional)
├── api/
│   └── routes/
│       └── agent.py       # Endpoint /agent/chat
├── core/
│   ├── logging_config.py  # Configuración de logs
│   ├── long_term_memory.py# Memoria a largo plazo (pgvector)
│   ├── mcp_client.py      # Cliente para el servidor MCP
│   └── memory.py          # Contexto de sesión (Redis)
├── db/
│   ├── base.py            # Engine y sesión de SQLAlchemy
│   └── model.py           # Modelo MemoryChunk
├── domain/
│   ├── agent_loop.py      # Bucle del agente (ReAct)
│   ├── harness.py         # Ejecutor de herramientas
│   ├── models.py          # Modelos Pydantic (AgentState, ToolCall...)
│   └── tools.py           # Registro de herramientas
├── logs/                  # Archivos de log
├── tools_server/
│   └── server.py          # Servidor FastMCP con las tools
├── alembic.ini
├── main.py                # Punto de entrada FastAPI y pruebas
├── init_db.py             # Script de creación de tablas
└── requirements.txt
🐞 Solución de problemas comunes
❌ ModuleNotFoundError: No module named 'sqlalchemy.func'
En db/model.py, reemplaza:

python
from sqlalchemy.func import now
por:

python
from sqlalchemy import func
Y usa default=func.now() en la columna created_at.

❌ relation "memory_chunks" does not exist
La tabla no ha sido creada. Ejecuta el script init_db.py (ver paso 5). Si ya lo hiciste, verifica que el contenedor de PostgreSQL esté corriendo:

bash
docker ps
Y comprueba la tabla:

bash
docker exec -it postgres-agentcore psql -U agent -d agentcore -c "\d memory_chunks"
❌ Docker Engine stopped
Abre Docker Desktop manualmente o, si usas WSL 2, ejecuta:

bash
wsl --shutdown
Y vuelve a iniciar Docker Desktop.

❌ alembic.util.messaging Target database is not up to date
Tienes migraciones viejas sin aplicar. Para desarrollo, puedes ignorar Alembic y usar init_db.py. Si insistes en Alembic, ejecuta:

bash
alembic stamp head
alembic revision --autogenerate -m "nueva migración"
alembic upgrade head
❌ Error al importar torch o sentence-transformers
Asegúrate de tener una versión de Python compatible (3.10–3.12). Si el error persiste, instala PyTorch CPU:

bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers
🔄 Diagrama de secuencia
El siguiente diagrama muestra el flujo completo de una petición al agente, desde que el usuario llama al endpoint hasta que recibe la respuesta final.

🧭 Lectura rápida del diagrama
Entrada: el usuario llama a POST /agent/chat con su mensaje y un session_id.

Inicialización: el bucle del agente prepara el estado, el harness y los permisos.

Contexto: se consulta Redis. Si es una sesión nueva, se recuperan memorias relevantes de pgvector y se inyectan como mensajes de sistema.

Bucle ReAct: se consulta a Ollama, se parsea la respuesta y, según sea una acción o una respuesta final, se ejecuta la herramienta o se cierra el ciclo.

Ejecución de tools: el harness valida permisos y argumentos antes de delegar al cliente MCP, que a su vez llama por SSE al servidor FastMCP. Las herramientas (calculator, get_date, search) se ejecutan allí y devuelven la observación.

Persistencia: al final, el resumen de la interacción se guarda en la memoria a largo plazo (pgvector) para futuras consultas.

Salida: FastAPI devuelve el AgentState con la respuesta final y el detalle de todos los pasos.

📝 Notas
El proyecto usa Python 3.15 en algunos entornos, pero no se recomienda para producción ni desarrollo estable. Usa 3.11 o 3.12.

Las herramientas son simuladas; search devuelve un resultado ficticio. Puedes extenderlas en domain/tools.py y tools_server/server.py.

Para producción, reemplaza eval en la calculadora por una librería segura como asteval o numexpr.

📄 Licencia
Este proyecto es de uso educativo. Puedes modificarlo y distribuirlo libremente.
