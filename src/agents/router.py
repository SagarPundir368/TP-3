"""Intent router: decides whether to start the flight/hotel/weather pipeline or the expense pipeline."""
from langchain_core.messages import SystemMessage, HumanMessage

from src.llm import llm_tool
from src.state import TravelState, RouterDecision


def route_user_query(state: TravelState) -> str:
    """
    Uses an LLM with structured output to semantically classify user intent
    and route to the correct starting node.
    """
    query = state['user_query']
    
    # 1. Bind the Pydantic schema to your LLM
    structured_router = llm_tool.with_structured_output(RouterDecision)
    
    # 2. System prompt guiding the classification
    system_prompt = (
        "You are an expert routing classifier for a Travel & Expense system. "
        "Analyze the user's input and determine whether their primary goal is: "
        "1. Logging, managing, or querying money/expenses -> 'expense_agent'\n"
        "2. Planning a journey, booking flights, hotels, or viewing an itinerary -> 'flight_agent'"
    )
    
    try:
        decision: RouterDecision = structured_router.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User Query: {query}")
        ])
        print(f"-> [Router] LLM selected route: {decision.next_node}")
        return decision.next_node
    except Exception as e:
        print(f"-> [Router] Fallback triggered due to error: {e}")
        # Safe fallback in case of an API issue
        return "flight_agent"
