from Agent_core.domain.agent_loop import run_agent
from Agent_core.core.logging_config import setup_logging
from fastapi import FastAPI
from Agent_core.api.routes.agent import router
if __name__ == "__main__":
    setup_logging()
    state = run_agent("¿Cuánto es 25 * 4?",session_id="test-002")
    
    print(f"Respuesta: {state.final_answer}")
    print(f"\n=== RESULTADO ===")
    print(f"Steps usados: {len(state.steps)}")
    
    print(f"\n=== STEPS ===")
    for i, step in enumerate(state.steps):
        print(f"\nStep {i+1}:")
        print(f"  Thought: {step.thought}")
        if step.action:
            print(f"  Action: {step.action.tool_name}")
            print(f"  Input: {step.action.input}")
        if step.observation:
            print(f"  Observation: {step.observation}")
        if step.is_final:
            print(f"  [FINAL]")
# Prueba 1 — tool que no existe
    state = run_agent("Busca el clima en Buenos Aires usando weather_tool",session_id="test-002")
    print(f"Respuesta: {state.final_answer}")
    print(f"\n=== RESULTADO ===")
    print(f"Steps usados: {len(state.steps)}")
        
    print(f"\n=== STEPS ===")
    for i, step in enumerate(state.steps):
        print(f"\nStep {i+1}:")
        print(f"  Thought: {step.thought}")
        if step.action:
            print(f"  Action: {step.action.tool_name}")
            print(f"  Input: {step.action.input}")
        if step.observation:
            print(f"  Observation: {step.observation}")
        if step.is_final:
            print(f"  [FINAL]")

# Prueba 2 — get_date
    state = run_agent("¿Qué día es hoy?","test-002")
    print(state.final_answer)   
    
    print(f"Respuesta: {state.final_answer}")
    print(f"\n=== RESULTADO ===")
    print(f"Steps usados: {len(state.steps)}")
            
    print(f"\n=== STEPS ===")
    for i, step in enumerate(state.steps):
        print(f"\nStep {i+1}:")
        print(f"  Thought: {step.thought}")
        if step.action:
            print(f"  Action: {step.action.tool_name}")
            print(f"  Input: {step.action.input}")
        if step.observation:
                print(f"  Observation: {step.observation}")
        if step.is_final:
                print(f"  [FINAL]")
                
app = FastAPI(title="AgentCore")
app.include_router(router)