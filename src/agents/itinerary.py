from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from src.prompts import ITINERARY_PROMPT
from src.state import TravelState
from src.llm import llm_reasoning


def itinerary_agent(state: TravelState):
    """
    Synthesizes the gathered flight, hotel, and weather data into a final, 
    comprehensive travel itinerary for the user.
    """
    print("[Agent] Running Itinerary Agent...\n")
    prompt = ITINERARY_PROMPT.format(
        query=state['user_query'],
        flight_results=state['flight_results'],
        hotel_results=state['hotel_results'],
        weather_results=state['weather_results']  
    )

    response = llm_reasoning.invoke([
        SystemMessage(content="You are an expert travel planner"),
        HumanMessage(content=prompt)
    ])

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

