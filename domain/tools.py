# domain/tools.py
from pydantic import BaseModel, Field
from typing import Callable, List, Type, Dict
from datetime import date

# 1. Definimos los Schemas de argumentos (Validación estricta)
class CalculatorArgs(BaseModel):
    expression: str = Field(..., description="Expresión matemática a evaluar. Ej: 2+2")

class SearchArgs(BaseModel):
    query: str = Field(..., description="Término de búsqueda")

class EmptyArgs(BaseModel):
    pass

# 2. El Manifiesto de la Tool
class ToolManifest(BaseModel):
    name: str
    description: str
    required_scopes: List[str]
    args_schema: Type[BaseModel]
    func: Callable
    class Config:
        arbitrary_types_allowed = True

# 3. Registro Global
TOOLS_REGISTRY: Dict[str, ToolManifest] = {}

def register_tool(manifest: ToolManifest) -> None:
    TOOLS_REGISTRY[manifest.name] = manifest

# 4. Funciones puras (no saben nada del harness)
def calculadora_(expression: str):
    return eval(expression)

def get_date_():
    return str(date.today())

def search_(query: str):
    return f"Resultado simulado para: {query}"

# 5. Registro de las tools con sus manifiestos
register_tool(ToolManifest(
    name="calculator",
    description="Evalúa expresiones matemáticas.",
    required_scopes=["execute:calculator"],
    args_schema=CalculatorArgs,
    func=calculadora_
))

register_tool(ToolManifest(
    name="get_date",
    description="Obtiene la fecha de hoy.",
    required_scopes=["execute:get_date"],
    args_schema=EmptyArgs,
    func=get_date_
))

register_tool(ToolManifest(
    name="search",
    description="Busca en un buscador.",
    required_scopes=["read:search"],
    args_schema=SearchArgs,
    func=search_
))