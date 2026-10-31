from pydantic import BaseModel
from typing import Optional
from typing import List

class ToolCall(BaseModel):
    tool_name: str
    input: dict          # ← cambio


class AgentStep(BaseModel):
    thought: str
    action: Optional[ToolCall] = None       # ← opcional
    observation: Optional[str] = None       # ← opcional
    is_final: bool = False                  # ← default


class AgentState(BaseModel):
    input: str
    steps: list[AgentStep] = []    # ← default lista vacía
    is_final: bool = False         # ← default
    final_answer: Optional[str] = None  # ← opcional
    
    
class ToolPermission(BaseModel):
    scopes:List[str]
    