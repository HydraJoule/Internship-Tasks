from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.graph.nodes import (
    detect_intent,
    retrieve_context,
    evaluate_context,
    generate_answer,
    handle_clarification,
    handle_fallback,
    escalate_to_human
)
from app.graph.routing import decide_next_step, decide_generation
from app.utils.logger import get_logger

logger = get_logger(__name__)

def build_workflow() -> StateGraph:
    logger.info("Building LangGraph workflow")
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("intent", detect_intent)
    workflow.add_node("retrieve", retrieve_context)
    workflow.add_node("evaluate", evaluate_context)
    workflow.add_node("generate", generate_answer)
    workflow.add_node("clarify", handle_clarification)
    workflow.add_node("fallback", handle_fallback)
    workflow.add_node("escalate", escalate_to_human)

    # Define edges
    workflow.set_entry_point("intent")

    # Conditional routing after intent detection
    workflow.add_conditional_edges(
        "intent",
        decide_next_step,
        {
            "retrieve": "retrieve",
            "clarify": "clarify",
            "escalate": "escalate"
        }
    )

    # After retrieval, evaluate context
    workflow.add_edge("retrieve", "evaluate")

    # Conditional routing after evaluation
    workflow.add_conditional_edges(
        "evaluate",
        decide_generation,
        {
            "generate": "generate",
            "fallback": "fallback"
        }
    )

    # Edges to END
    workflow.add_edge("generate", END)
    workflow.add_edge("clarify", END)
    workflow.add_edge("fallback", END)
    workflow.add_edge("escalate", END)

    return workflow.compile()

compiled_graph = build_workflow()
