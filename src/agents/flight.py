"""Flight recommendation agent."""

import asyncio
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, AnyMessage
from src.llm import llm_reasoning
from src.prompts import FLIGHT_AGENT_PROMPT
from src.mcp_client import aviation_mcp_call
from src.state import TravelState



def flight_agent(state: TravelState):
    """
    Retrieves available airports and airlines using Aviation MCP tools, 
    then uses the LLM to recommend suitable flight options based on the user's query.
    """
    print("\n[Agent] Running Flight Agent...")
    query = state['user_query']

    try:
        # Fetch data via synchronous wrappers for MCP async calls
        airports = asyncio.run(aviation_mcp_call("list_airports"))
        airlines = asyncio.run(aviation_mcp_call("list_airlines"))

        prompt = FLIGHT_AGENT_PROMPT.format(
            query=query,
            airport_data=str(airports)[:3000],
            airline_data=str(airlines)[:3000]
        )

        response = llm_reasoning.invoke([
            SystemMessage(content="You are an expert travel flight planner"),
            HumanMessage(content=prompt)
        ])
        flight_data = response.content

    except Exception as e:
        flight_data = f"Flight information unavailable: {str(e)}"

    return {
        "flight_results": flight_data,
        "messages": [AIMessage(content="Flight recommendation generated")],
        "llm_calls": state.get("llm_calls", 0) + 1
    }
