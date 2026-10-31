from pydantic import BaseModel
from typing import List,Optional
from domain.models import AgentStep
class StepResponse(BaseModel):
    thought: str
    action_name: Optional[str] = None    # el nombre de la tool usada
    action_input: Optional[dict] = None  # los argumentos
    observation: Optional[str] = None
    is_final: bool = False

class ChatRequest(BaseModel):
    session_id:str
    message:str
class ChatResponse(BaseModel):
    session_id: str
    answer: str
    steps_used: int
    step_response:List[StepResponse]
    
def step_to_response(step:AgentStep):
    return StepResponse(
        thought=step.thought,
        action_name=step.action.tool_name if step.action else None,
        action_input=step.action.input if step.action else None,
        observation=step.observation,
        is_final=step.is_final
    )