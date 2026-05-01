import json
import os
from typing import Dict, Any
from app.config import settings

ESCALATION_FILE = os.path.join(settings.UPLOAD_DIR, "escalations.json")

def create_escalation_ticket(state_data: Dict[str, Any]) -> str:
    """
    Creates an escalation ticket in a local JSON file (simulating a database).
    Returns ticket ID.
    """
    import uuid
    ticket_id = str(uuid.uuid4())
    
    ticket = {
        "ticket_id": ticket_id,
        "query": state_data.get("user_query"),
        "intent": state_data.get("intent"),
        "confidence": state_data.get("confidence_score", 0.0),
        "reason": state_data.get("escalation_reason", "Manual Escalation"),
        "status": "pending",
        "human_decision": None
    }
    
    # Load existing
    escalations = []
    if os.path.exists(ESCALATION_FILE):
        with open(ESCALATION_FILE, "r") as f:
            try:
                escalations = json.load(f)
            except json.JSONDecodeError:
                pass
                
    escalations.append(ticket)
    with open(ESCALATION_FILE, "w") as f:
        json.dump(escalations, f, indent=2)
        
    return ticket_id
