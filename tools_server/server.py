from fastmcp import FastMCP
from datetime import date

mcp = FastMCP(name="AgentCore Tools")

@mcp.tool
def calculator(expression: str) -> str:
    """Evalúa expresiones matemáticas."""
    return eval(expression)

@mcp.tool
def get_date() -> str:
    """Retorna la fecha de hoy."""
    return str(date.today())

@mcp.tool  
def search(query: str) -> str:
    """Busca información dado una query."""
    return f"Resultado simulado para: {query}"

if __name__ == "__main__":
    if __name__ == "__main__":
        mcp.run(transport="streamable-http", host="0.0.0.0", port=8001)