
import re
from Agent_core.domain.models import AgentState, AgentStep, ToolCall,ToolPermission
from Agent_core.domain.tools import TOOLS_REGISTRY
from Agent_core.domain.harness import ToolHarness
import json
from Agent_core.domain.models import AgentStep, ToolCall
import ollama
from Agent_core.core.memory import ContextWindow
from Agent_core.core.long_term_memory import LongTermMemory

system_prompt = """You are a helpful assistant with access to tools.

To answer the user's question, follow this EXACT format:

Thought: [your reasoning about what to do next]
Action: [tool name — exactly as listed below]
Action Input: {"key": "value"}

After receiving the Observation, continue with:
Thought: [your reasoning]
Action: [next tool if needed]
Action Input: {"key": "value"}

When you have enough information to answer, use:
Thought: [I now have the answer]
Final Answer: [your response to the user]

Available tools:
- calculator: Evalúa expresiones matemáticas. Input: {{"expression": "2+2"}}
- get_date: Retorna la fecha del dia Actual. Input: {{}}
- search: Busca en un buscador la informacion dada por la query. Input: {{"query": "tu búsqueda"}}

IMPORTANT:
- NEVER answer from memory. ALWAYS use a tool to get real data.
- Always start with Thought:
- Never skip the Thought before an Action
- Use exactly the tool names listed above
- Always end with Final Answer:
"""


def parse_llm_response(text: str) -> AgentStep:
    lines = text.strip().split("\n")
    
    
    
    # Caso 1: tiene Final Answer
    if "Final Answer:" in text:
        thought = ""
        final_answer = ""
        for line in lines:
            if line.startswith("Thought:"):
                thought = line.replace("Thought:", "").strip()
            if line.startswith("Final Answer:"):
                final_answer = line.replace("Final Answer:", "").strip()
        return AgentStep(
            thought=thought,
            observation=final_answer,
            is_final=True
        )
    
    # Caso 2: tiene Action
    thought = ""
    tool_name = ""
    tool_input = {}
    for line in lines:
        
        
        if line.startswith("Thought:"):
            thought = line.replace("Thought:", "").strip()
        if line.startswith("Action:"):
            tool_name = line.replace("Action:", "").strip()
        if line.startswith("Action Input:"):
            raw = line.replace("Action Input:", "").strip()
            try:
                tool_input=json.loads(raw)
            except:
                tool_input={}# convierte string a dict
    
    return AgentStep(
        thought=thought,
        action=ToolCall(tool_name=tool_name, input=tool_input),
        is_final=False
    )




def run_agent(user_input: str, session_id: str, max_steps: int = 5) -> AgentState:
    state = AgentState(input=user_input)
    harness = ToolHarness()
    agent_permission = ToolPermission(
        scopes=["read:search", "execute:calculator", "execute:get_date"]
    )
    
    # Usar ContextWindow en vez de lista local
    context = ContextWindow(session_id=session_id)
    ltm=LongTermMemory()
    # Agregar el system prompt y el mensaje del usuario
    if len(context.get_messages())==0:
        context.add_message("system", system_prompt)
        memories = ltm.retrieve(user_input, top_k=3)
        if memories:
            memory_text = "\n".join(f"- {m}" for m in memories)
            context.add_message("system", f"Relevant memories:\n{memory_text}")

    context.add_message("user", user_input)
    
    while not state.is_final and len(state.steps) < max_steps:
        
        # Obtener mensajes desde Redis
        messages = context.get_messages()
        
        response = ollama.chat(model="llama3.2", messages=messages)
        llm_text = response["message"]["content"]
        
        step = parse_llm_response(llm_text)
        
        if step.is_final:
            state.is_final = True
            state.final_answer = step.observation
        else:
            tool_name = step.action.tool_name
            if tool_name not in TOOLS_REGISTRY:
                step.observation = f"Tool not found: '{tool_name}'. Available: {list(TOOLS_REGISTRY.keys())}"
            else:
                step.observation = str(harness.execute(step.action, agent_permission))
            
            # Guardar en Redis en vez de lista local
            context.add_message("assistant", llm_text)
            context.add_message("user", f"Observation: {step.observation}")
        
        state.steps.append(step)
    
    if not state.is_final:
        state.final_answer = "No se puede completar la tarea en el numero maximo de pasos."
    ltm.store(
        session_id=session_id,
        content=f"User asked: {user_input}. Agent answered: {state.final_answer}"
    )

    
    return state
    
