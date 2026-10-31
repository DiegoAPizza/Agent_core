from fastapi import APIRouter, HTTPException
from api.schemas.chat import ChatRequest, ChatResponse, StepResponse, step_to_response
from domain.agent_loop import run_agent
from core.memory import ContextWindow

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # 1. correr el agente con request.message
    respuesta_del_agente=run_agent(request.message,request.session_id);
    
    # 2. convertir state.steps → List[StepResponse] usando step_to_response
    
    respuesta_agente=[ step_to_response(step) for step in respuesta_del_agente.steps]
    # 3. retornar ChatResponse
    respuesta_usuario=ChatResponse(session_id=request.session_id,answer=respuesta_del_agente.final_answer,steps_used=len(respuesta_del_agente.steps),step_response=respuesta_agente)
   
    return respuesta_usuario

@router.get("/sessions/{session_id}/history")
def get_history(session_id: str):
    context = ContextWindow(session_id=session_id)
    return {
        "session_id": session_id,
        "history": context.get_messages()
    }