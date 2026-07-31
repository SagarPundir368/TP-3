# ==========================================
# 1. IMPORTS
# ==========================================
import os
import asyncio
import operator
from typing import TypedDict, Annotated

import psycopg
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, AnyMessage
from langchain_groq import ChatGroq

# Local MCP tool imports
from agents.mcp_client import (
    tavily_mcp_search,
    aviation_mcp_call,
    get_airlines, 
    get_airport,
    weather_mcp_search,
    forecast_mcp_search,
    extract_destination
)

# Local prompt imports
from agents.prompts import FLIGHT_AGENT_PROMPT, ITINERARY_PROMPT

# ==========================================
# 2. CONFIGURATION & SETUP
# ==========================================
load_dotenv()

LLM_API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Initialize the Groq LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=LLM_API_KEY
)

# ==========================================
# 3. GRAPH STATE DEFINITION
# ==========================================
class TravelState(TypedDict):
    """
    Represents the state of the workflow as it moves through the graph nodes.
    """
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    weather_results: str
    itinerary: str
    llm_calls: int


# ==========================================
# 4. AGENT NODES (Functions)
# ==========================================
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

        response = llm.invoke([
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

    response = llm.invoke([
        SystemMessage(content="You are an expert travel planner"),
        HumanMessage(content=prompt)
    ])

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }


# ==========================================
# 5. GRAPH CONSTRUCTION
# ==========================================
def build_travel_graph():
    """
    Initializes the LangGraph state graph, adds all agent nodes, 
    and defines the execution edges (workflow path).
    """
    graph = StateGraph(TravelState)

    # Add Nodes
    graph.add_node("flight_agent", flight_agent)
    graph.add_node("hotel_agent", hotel_agent)
    graph.add_node("weather_agent", weather_agent)
    graph.add_node("itinerary_agent", itinerary_agent)

    # Define Edges (Workflow flow)
    graph.add_edge(START, "flight_agent")
    graph.add_edge("flight_agent", "hotel_agent")
    graph.add_edge("hotel_agent", "weather_agent")
    graph.add_edge("weather_agent", "itinerary_agent")
    graph.add_edge("itinerary_agent", END)
    
    return graph

def get_compiled_app():
    """
    Initializes the Database and returns the compiled app globally for Streamlit.
    """
    conn = psycopg.connect(DATABASE_URL, autocommit=True)
    checkpointer = PostgresSaver(conn)
    checkpointer.setup()
    
    graph = build_travel_graph()
    return graph.compile(checkpointer=checkpointer)

# ==========================================
# 6. MAIN EXECUTION
# ==========================================
def main():
    """
    Sets up the PostgreSQL checkpointer, compiles the graph, 
    takes user input, and invokes the travel workflow.
    """
    # 1. Setup Database Connection & Checkpointer
    # Handled locally here so it doesn't execute simply by importing the file
    app = get_compiled_app()

    # 3. Configure Thread Context for Memory
    config = {
        'configurable': {
            'thread_id': 'user_sagar'
        }
    }

    # 4. Get Input and Invoke Workflow
    user_input = input("Enter travel request: ")

    result = app.invoke(
        {
            'messages': [HumanMessage(content=user_input)],
            'user_query': user_input,
            'flight_results': "",
            'hotel_results': "",
            'weather_results': "",
            'itinerary': "",
            'llm_calls': 0
        },
        config=config
    )

    # 5. Display Final Result
    print("\n====================================")
    print("          FINAL RESPONSE            ")
    print("====================================")
    
    # We generally only want to print the final itinerary message 
    # (the last item) rather than intermediate AIMessage logs.
    for msg in result['messages']:
        print(f"- {msg.content}")

if __name__ == "__main__":
    main()