import json
import logging
from pydantic import ValidationError
from Agent_core.domain.models import ToolCall, ToolPermission
from Agent_core.domain.tools import TOOLS_REGISTRY
from Agent_core.core.mcp_client import MCPToolClient
logger = logging.getLogger("agentcore.harness")

class ToolHarness:
    def execute(self, tool_call: ToolCall, permissions: ToolPermission) -> str:
        # 1. Verificar si existe
        if tool_call.tool_name not in TOOLS_REGISTRY:
            return f"Error: Tool '{tool_call.tool_name}' not found."
        
        tool = TOOLS_REGISTRY[tool_call.tool_name]
        
        # 2. Verificar permisos
        has_permission = all(scope in permissions.scopes for scope in tool.required_scopes)
        if not has_permission:
            logger.warning(json.dumps({
                "event": "permission_denied", 
                "tool": tool_call.tool_name,
                "required": tool.required_scopes,
                "has": permissions.scopes
            }))
            return "Error: Permission denied. You do not have the required scopes to use this tool."
        
        # 3. Validar argumentos
        try:
            validated_args = tool.args_schema(**tool_call.input)
        except ValidationError as e:
            return f"Error de validación de argumentos: {e.json()}"
            
        # 4. Loggear intención
        logger.info(json.dumps({
            "event": "tool_execution",
            "tool": tool_call.tool_name,
            "args": tool_call.input
        }))
        
        # 5. Ejecutar
        try:
            # Usamos model_dump() para pasar los args validados
            mcp_client = MCPToolClient()
            result = mcp_client.call_tool(tool_call.tool_name, tool_call.input)
            logger.info(json.dumps({
                "event": "tool_result",
                "tool": tool_call.tool_name,
                "result": str(result)
                }))
            return str(result)
        except Exception as e:
            return f"Error ejecutando la tool: {str(e)}"