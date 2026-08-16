from typing import TypedDict, Any, Annotated, Literal
from pydantic import BaseModel, Field
import operator
from langchain_core.messages import AnyMessage

## GRAPH NODE'S STATE
class TravelState(TypedDict):
    """
    Represents the state of the workflow as it moves through the graph nodes.
    """
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    weather_results: str
    expense_results: str
    itinerary: str
    llm_calls: int

## ROUTER NODE'S LLM OUTPUT SCHEMA
class RouterDecision(BaseModel):
    """Schema to route the user query to the appropriate agent workflow."""
    next_node: Literal["expense_agent", "flight_agent"] = Field(
        description=(
            "Choose 'expense_agent' if the user wants to add, log, track, list, or summarize expenses, money, payments, or costs. "
            "Choose 'flight_agent' if the user is asking to plan a trip, search flights, find hotels, check weather, or build an itinerary."
        )
    )
