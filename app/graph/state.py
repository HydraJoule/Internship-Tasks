from typing import TypedDict, List, Dict, Any, Optional

class GraphState(TypedDict, total=False):
    session_id: str
    uploaded_files: List[str]
    user_query: str
    normalized_query: str
    intent: str
    retrieved_chunks: List[Dict[str, Any]]
    context_sufficient: bool
    answer_draft: str
    confidence_score: float
    route: str
    escalation_required: bool
    escalation_reason: str
    human_decision: Optional[str]
    final_response: str
    sources: List[str]
    error: Optional[str]
