"""Weather & forecast agent."""

import asyncio
from langchain_core.messages import AIMessage
from src.prompts import FLIGHT_AGENT_PROMPT
from src.mcp_client import weather_mcp_search, forecast_mcp_search
from src.frontend.utils import extract_destination
from src.state import TravelState


def weather_agent(state: TravelState):
    """
    Extracts the destination city from the query and fetches the current weather 
    and forecast using the custom Weather MCP server.
    """
    print("[Agent] Running Weather Agent...")
    city = extract_destination(state['user_query'])

    weather_data = asyncio.run(weather_mcp_search(city))
    forecast_data = asyncio.run(forecast_mcp_search(city))

    formatted_weather = f"""
    Current Weather:
    {weather_data}

    Forecast:
    {forecast_data}
    """

    return {
        "weather_results": formatted_weather,
        "messages": [AIMessage(content="Weather Information Fetched")]
    }
