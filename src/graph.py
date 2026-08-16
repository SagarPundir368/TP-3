# import psycopg
# from langgraph.checkpoint.postgres import PostgresSaver
# from langgraph.graph import END, START, StateGraph

# from src import (
#     budget_agent,
#     final_response_agent,
#     flight_agent,
#     hotel_agent,
#     human_approval_agent,
#     itinerary_agent,
#     supervisor_agent,
#     weather_agent,
# )
# from config import DATABASE_URL
# from src.state import TravelState

# AGENT_ORDER = [
#     "flight_agent",
#     "hotel_agent",
#     "weather_agent",
#     "budget_agent",
#     "itinerary_agent",
# ]

# ROUTE_MAP = {
#     "flight_agent": "flight_agent",
#     "hotel_agent": "hotel_agent",
#     "weather_agent": "weather_agent",
#     "budget_agent": "budget_agent",
#     "itinerary_agent": "itinerary_agent",
# }


# def _selected_agents(state: TravelState) -> list[str]:
#     selected = state.get("selected_agents")
#     return [agent for agent in AGENT_ORDER if agent in selected]  


# def route_from_supervisor(state: TravelState) -> str:
#     selected = _selected_agents(state)
#     return selected[0] if selected else "itinerary_agent"


# def route_after_agent(current_agent: str):
#     def route(state: TravelState) -> str:
#         selected = _selected_agents(state)
#         current_index = AGENT_ORDER.index(current_agent)

#         for next_agent in AGENT_ORDER[current_index + 1:]:
#             if next_agent in selected:
#                 return next_agent

#         return "itinerary_agent"

#     return route


# def build_graph():
#     graph = StateGraph(TravelState)

#     graph.add_node("supervisor", supervisor_agent)
#     graph.add_node("flight_agent", flight_agent)
#     graph.add_node("hotel_agent", hotel_agent)
#     graph.add_node("weather_agent", weather_agent)
#     graph.add_node("budget_agent", budget_agent)
#     graph.add_node("itinerary_agent", itinerary_agent)
#     graph.add_node("human_approval", human_approval_agent)
#     graph.add_node("final_response", final_response_agent)

#     graph.add_edge(START, "supervisor")
#     graph.add_conditional_edges("supervisor", route_from_supervisor, ROUTE_MAP)
#     graph.add_conditional_edges("flight_agent", route_after_agent("flight_agent"), ROUTE_MAP)
#     graph.add_conditional_edges("hotel_agent", route_after_agent("hotel_agent"), ROUTE_MAP)
#     graph.add_conditional_edges("weather_agent", route_after_agent("weather_agent"), ROUTE_MAP)
#     graph.add_conditional_edges("budget_agent", route_after_agent("budget_agent"), ROUTE_MAP)
#     graph.add_edge("itinerary_agent", "human_approval")
#     graph.add_edge("human_approval", "final_response")
#     graph.add_edge("final_response", END)

#     if DATABASE_URL:
#         conn = psycopg.connect(DATABASE_URL)
#         checkpointer = PostgresSaver(conn)
#         checkpointer.setup()
#         return graph.compile(checkpointer=checkpointer)

#     return graph.compile()


# app = build_graph()

"""LangGraph construction & compilation for the Travel & Expense workflow."""
import os
import sqlite3

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from src.state import TravelState
from src.agents import (
    flight_agent,
    hotel_agent,
    weather_agent,
    expense_agent,
    itinerary_agent,
    route_user_query,
)

DB_PATH = "data/agents.db"


def build_travel_graph() -> StateGraph:
    """Builds the graph: adds all agent nodes and defines the execution edges (workflow path)."""
    graph = StateGraph(TravelState)

    graph.add_node("flight_agent", flight_agent)
    graph.add_node("hotel_agent", hotel_agent)
    graph.add_node("weather_agent", weather_agent)
    graph.add_node("expense_agent", expense_agent)
    graph.add_node("itinerary_agent", itinerary_agent)

    graph.add_conditional_edges(
        START,
        route_user_query,
        {
            "expense_agent": "expense_agent",
            "flight_agent": "flight_agent",
        },
    )
    graph.add_edge("expense_agent", END)
    graph.add_edge("flight_agent", "hotel_agent")
    graph.add_edge("hotel_agent", "weather_agent")
    graph.add_edge("weather_agent", "itinerary_agent")
    graph.add_edge("itinerary_agent", END)

    return graph


def get_compiled_app():
    """Sets up the SQLite checkpointer and returns the compiled graph (used by Streamlit too)."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    graph = build_travel_graph()
    return graph.compile(checkpointer=checkpointer)
