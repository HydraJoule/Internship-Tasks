import json
import os
from typing import Dict, List
from app.hitl.escalation import ESCALATION_FILE

def get_pending_escalations() -> List[Dict]:
    if not os.path.exists(ESCALATION_FILE):
        return []
    with open(ESCALATION_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def resolve_escalation(ticket_id: str, decision: str):
    escalations = get_pending_escalations()
    for t in escalations:
        if t["ticket_id"] == ticket_id:
            t["status"] = "resolved"
            t["human_decision"] = decision
            break
            
    with open(ESCALATION_FILE, "w") as f:
        json.dump(escalations, f, indent=2)
