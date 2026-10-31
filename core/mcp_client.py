from fastmcp import Client
import asyncio

class MCPToolClient:
    def __init__(self, url: str = "http://localhost:8001"):
        self.url = url
    
    def call_tool(self, tool_name: str, tool_input: dict) -> str:
        # FastMCP usa async, necesitamos correrlo en sync
        return asyncio.run(self._call(tool_name, tool_input))
    
    async def _call(self, tool_name: str, tool_input: dict) -> str:
        async with Client(self.url) as client:
            result = await client.call_tool(tool_name, tool_input)
            return str(result[0].text)
    
    def list_tools(self) -> list[str]:
        return asyncio.run(self._list())
    
    async def _list(self) -> list[str]:
        async with Client(self.url) as client:
            tools = await client.list_tools()
            return [t.name for t in tools]