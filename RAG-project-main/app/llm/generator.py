import json
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from app.config import settings
from app.llm.prompts import ROUTING_PROMPT, EVALUATION_PROMPT, ANSWER_PROMPT, CLARIFY_PROMPT
from app.utils.logger import get_logger

logger = get_logger(__name__)

class LLMService:
    def __init__(self):
        logger.info(f"Initializing Groq LLM: {settings.MODEL_NAME}")
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY, 
            model_name=settings.MODEL_NAME, 
            temperature=0.0
        )
            
    def analyze_routing(self, query: str) -> dict:
        prompt = ROUTING_PROMPT.format(query=query)
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)]).content
            # Extract JSON block robustly
            start_idx = response.find("{")
            end_idx = response.rfind("}")
            if start_idx != -1 and end_idx != -1:
                return json.loads(response[start_idx:end_idx+1])
            
            logger.error(f"Routing logic failed: No JSON block found in response: {response}")
            return {"intent": "unknown", "route": "answer"} # default to answer when in doubt
        except Exception as e:
            logger.error(f"Routing logic failed: {e} | Response was: {response}")
            return {"intent": "unknown", "route": "answer"}

    def evaluate_context(self, query: str, context: str) -> bool:
        prompt = EVALUATION_PROMPT.format(query=query, context=context)
        response = self.llm.invoke([HumanMessage(content=prompt)]).content.strip().upper()
        # Make the LLM parsing much more robust against conversational fluff like "YES." or "Based on context, YES"
        if "YES" in response or "TRUE" in response:
            return True
        elif "NO" in response or "FALSE" in response:
            return False
        # Default to True if it's ambiguous, letting the final Answer generation node handle it gracefully
        return True

    def generate_answer(self, query: str, context: str) -> str:
        prompt = ANSWER_PROMPT.format(query=query, context=context)
        return self.llm.invoke([HumanMessage(content=prompt)]).content

    def generate_clarification(self, query: str) -> str:
        prompt = CLARIFY_PROMPT.format(query=query)
        return self.llm.invoke([HumanMessage(content=prompt)]).content
