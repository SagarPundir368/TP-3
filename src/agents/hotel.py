"""Hotel search agent."""

import asyncio
from langchain_core.messages import AIMessage

from src.state import TravelState
from src.mcp_client import tavily_mcp_search


def hotel_agent(state: TravelState):
    """
    Searches the web for the best hotel accommodations tailored to the user's destination.
    """
    print("[Agent] Running Hotel Agent...")
    query = f"Best hotels for {state['user_query']}"
    
    hotel_results = asyncio.run(tavily_mcp_search(query))
    
    return {
        "hotel_results": hotel_results,
        "messages": [AIMessage(content="Hotel Information Fetched")],
        "llm_calls": state.get("llm_calls", 0) + 1
    }
