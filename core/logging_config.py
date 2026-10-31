import logging
import os

def setup_logging():
    # 1. Crear carpeta si no existe
    os.makedirs("logs", exist_ok=True)
    
    # 2. Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 3. Handler de consola — imprime en pantalla
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 4. Handler de archivo — guarda en logs/agent.log
    file_handler = logging.FileHandler("logs/agent.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    
    # 5. Logger raíz
    logger = logging.getLogger("agentcore")
    logger.setLevel(logging.DEBUG)  # ← qué nivel? DEBUG, INFO, WARNING?
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger