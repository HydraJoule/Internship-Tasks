from app.graph.state import GraphState
from app.llm.generator import LLMService
from app.rag.retriever import ContextRetriever
from app.hitl.escalation import create_escalation_ticket

llm_service = LLMService()
retriever = ContextRetriever()

def detect_intent(state: GraphState) -> GraphState:
    query = state.get("user_query", "")
    analysis = llm_service.analyze_routing(query)
    
    state["intent"] = analysis.get("intent", "unknown")
    state["route"] = analysis.get("route", "answer")
    return state

def retrieve_context(state: GraphState) -> GraphState:
    if state.get("route") != "answer":
        return state
        
    chunks = retriever.retrieve_for_session(state.get("session_id", ""), state.get("user_query", ""))
    state["retrieved_chunks"] = chunks
    
    # Deduplicate sources
    sources = set()
    for c in chunks:
        src = c["metadata"].get("source", "unknown")
        pg = c["metadata"].get("page", "?")
        sources.add(f"{src} (Page {pg})")
    
    state["sources"] = list(sources)
    return state

def evaluate_context(state: GraphState) -> GraphState:
    if state.get("route") != "answer":
        return state
        
    chunks = state.get("retrieved_chunks", [])
    if not chunks:
        state["context_sufficient"] = False
        state["route"] = "fallback"
        return state
        
    context_str = "\n\n".join([c["text"] for c in chunks])
    sufficient = llm_service.evaluate_context(state.get("user_query", ""), context_str)
    
    state["context_sufficient"] = sufficient
    if not sufficient:
        state["route"] = "fallback"
        
    return state

def generate_answer(state: GraphState) -> GraphState:
    if state.get("route") != "answer" or not state.get("context_sufficient"):
        return state
        
    context_str = "\n\n".join([c["text"] for c in state.get("retrieved_chunks", [])])
    answer = llm_service.generate_answer(state.get("user_query", ""), context_str)
    
    state["answer_draft"] = answer
    state["final_response"] = answer
    return state

def handle_clarification(state: GraphState) -> GraphState:
    answer = llm_service.generate_clarification(state.get("user_query", ""))
    state["final_response"] = answer
    return state

def handle_fallback(state: GraphState) -> GraphState:
    state["final_response"] = "I'm sorry, I don't see enough information in the uploaded documents to confidently answer your question."
    return state

def escalate_to_human(state: GraphState) -> GraphState:
    state["escalation_required"] = True
    create_escalation_ticket(state)
    state["final_response"] = "Your request has been escalated to a human agent for further review. They will get back to you shortly."
    return state
