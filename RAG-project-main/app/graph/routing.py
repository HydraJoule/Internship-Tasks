from app.graph.state import GraphState

def decide_next_step(state: GraphState) -> str:
    """
    Decides the next node based on intent and route from LLM.
    """
    route = state.get("route", "answer")
    
    if route == "clarify":
        return "clarify"
    if route == "escalate":
        return "escalate"
        
    return "retrieve"

def decide_generation(state: GraphState) -> str:
    """
    Decides whether to generate an answer or fallback based on retrieved context.
    """
    if state.get("route") == "fallback" or not state.get("context_sufficient"):
        return "fallback"
        
    return "generate"
