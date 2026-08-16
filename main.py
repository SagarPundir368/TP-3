# ==========================================
# 1. IMPORTS
# # ==========================================
# import os
# import asyncio
# import operator
# from typing import TypedDict, Annotated, Literal
# from pydantic import BaseModel, Field
# from dotenv import load_dotenv
# import sqlite3
# from langgraph.graph import StateGraph, START, END
# from langgraph.checkpoint.sqlite import SqliteSaver
# from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, AnyMessage
# from langchain_groq import ChatGroq
# from langchain_core.runnables import RunnableConfig
# import datetime


# # Local MCP tool imports
# from src.mcp_client import (
#     tavily_mcp_search,
#     aviation_mcp_call,
#     get_airlines, 
#     get_airport,
#     weather_mcp_search,
#     forecast_mcp_search,
#     extract_destination,
#     get_mcp_tool
# )

# # Local prompt imports
# from src.prompts import FLIGHT_AGENT_PROMPT, ITINERARY_PROMPT, EXPENSE_AGENT_PROMPT
# from src.state import TravelState, RouterDecision
# # ==========================================
# # 2. CONFIGURATION & SETUP
# # ==========================================

# from config import GROQ_API_KEY, DATABASE_URL,get_llm


# # Initialize the Groq LLM
# llm_tool, llm_reasoning = get_llm()

# ==========================================
# 3. GRAPH STATE DEFINITION
# ==========================================
# class TravelState(TypedDict):
#     """
#     Represents the state of the workflow as it moves through the graph nodes.
#     """
#     messages: Annotated[list[AnyMessage], operator.add]
#     user_query: str
#     flight_results: str
#     hotel_results: str
#     weather_results: str
#     expense_results: str
#     itinerary: str
#     llm_calls: int


# class RouterDecision(BaseModel):
#     """Schema to route the user query to the appropriate agent workflow."""
#     next_node: Literal["expense_agent", "flight_agent"] = Field(
#         description=(
#             "Choose 'expense_agent' if the user wants to add, log, track, list, or summarize expenses, money, payments, or costs. "
#             "Choose 'flight_agent' if the user is asking to plan a trip, search flights, find hotels, check weather, or build an itinerary."
#         )
#     )


# ==========================================
# 4. AGENT NODES (Functions)
# ==========================================
# def flight_agent(state: TravelState):
#     """
#     Retrieves available airports and airlines using Aviation MCP tools, 
#     then uses the LLM to recommend suitable flight options based on the user's query.
#     """
#     print("\n[Agent] Running Flight Agent...")
#     query = state['user_query']

#     try:
#         # Fetch data via synchronous wrappers for MCP async calls
#         airports = asyncio.run(aviation_mcp_call("list_airports"))
#         airlines = asyncio.run(aviation_mcp_call("list_airlines"))

#         prompt = FLIGHT_AGENT_PROMPT.format(
#             query=query,
#             airport_data=str(airports)[:3000],
#             airline_data=str(airlines)[:3000]
#         )

#         response = llm_reasoning.invoke([
#             SystemMessage(content="You are an expert travel flight planner"),
#             HumanMessage(content=prompt)
#         ])
#         flight_data = response.content

#     except Exception as e:
#         flight_data = f"Flight information unavailable: {str(e)}"

#     return {
#         "flight_results": flight_data,
#         "messages": [AIMessage(content="Flight recommendation generated")],
#         "llm_calls": state.get("llm_calls", 0) + 1
#     }

# def hotel_agent(state: TravelState):
#     """
#     Searches the web for the best hotel accommodations tailored to the user's destination.
#     """
#     print("[Agent] Running Hotel Agent...")
#     query = f"Best hotels for {state['user_query']}"
    
#     hotel_results = asyncio.run(tavily_mcp_search(query))
    
#     return {
#         "hotel_results": hotel_results,
#         "messages": [AIMessage(content="Hotel Information Fetched")],
#         "llm_calls": state.get("llm_calls", 0) + 1
#     }

# def weather_agent(state: TravelState):
#     """
#     Extracts the destination city from the query and fetches the current weather 
#     and forecast using the custom Weather MCP server.
#     """
#     print("[Agent] Running Weather Agent...")
#     city = extract_destination(state['user_query'])

#     weather_data = asyncio.run(weather_mcp_search(city))
#     forecast_data = asyncio.run(forecast_mcp_search(city))

#     formatted_weather = f"""
#     Current Weather:
#     {weather_data}

#     Forecast:
#     {forecast_data}
#     """

#     return {
#         "weather_results": formatted_weather,
#         "messages": [AIMessage(content="Weather Information Fetched")]
#     }

# def expense_agent(state: TravelState, config: RunnableConfig):
#     """
#     Handles financial requests, logging expenses, or summarizing costs using the native Expense MCP.
#     """
#     print("[Agent] Running Expense Agent...\n")
#     query = state['user_query']

#     # 1. Extract the thread_id securely from the LangGraph config
#     current_thread = config.get("configurable", {}).get("thread_id", "unknown_user")

#     # 2. Pass both the query, thread_id and today's date to the prompt
#     today_date = datetime.datetime.now().strftime("%Y-%m-%d")

#     prompt = EXPENSE_AGENT_PROMPT.format(
#         query=query, 
#         thread_id=current_thread,
#         current_date=today_date
#     )
#     # 1. Fetch the NATIVE tools directly from the MCP Client
#     mcp_add_tool = asyncio.run(get_mcp_tool("add_expense"))
#     mcp_list_tool = asyncio.run(get_mcp_tool("list_expenses"))
#     mcp_summarize_tool = asyncio.run(get_mcp_tool("summarize"))

#     # 2. Bind the native tools to the LLM
#     tools = [mcp_add_tool, mcp_list_tool, mcp_summarize_tool]
#     llm_with_tools = llm_tool.bind_tools(tools)

#     # 3. Invoke using the bound LLM
#     response = llm_with_tools.invoke([
#         SystemMessage(content="You are an expert travel finance manager. You MUST use the provided tools to save or retrieve data. DO NOT write raw SQL."),
#         HumanMessage(content=prompt)
#     ])

#     # 4. Intercept and execute the tool call if the LLM made one
#     if response.tool_calls:
#         results = []
#         for tool_call in response.tool_calls:
#             tool_name = tool_call["name"]
#             tool_args = tool_call["args"]
            
#             print(f"-> [System] LLM triggered tool: {tool_name}")

#             def extract_clean_text(raw_res):
#                 # Check if it is a list and contains the 'text' key
#                 if isinstance(raw_res, list) and len(raw_res) > 0 and 'text' in raw_res[0]:
#                     return raw_res[0]['text']
#                 return str(raw_res)
            
#             # Execute the native MCP tools using their built-in ainvoke method
#             if tool_name == "add_expense":
#                 raw_res = asyncio.run(mcp_add_tool.ainvoke(tool_args))
#                 clean_text = extract_clean_text(raw_res)
#                 results.append(f"✅ Successfully logged expense! Details:\n```json\n{clean_text}\n```")

#             elif tool_name == "list_expenses":
#                 raw_res = asyncio.run(mcp_list_tool.ainvoke(tool_args))
#                 clean_text = extract_clean_text(raw_res)
#                 results.append(f"📊 Expense List:\n{clean_text}")
            
#             elif tool_name == "summarize":
#                 raw_res = asyncio.run(mcp_summarize_tool.ainvoke(tool_args))
#                 clean_text = extract_clean_text(raw_res)
#                 results.append(f"💰 Expense Summary:\n{clean_text}")
        
#         final_text = "\n\n".join(results)
        
#         return {
#             "expense_results": final_text,
#             "messages": [AIMessage(content=final_text)],
#             "llm_calls": state.get("llm_calls", 0) + 1
#         }
        
#     else:
#         # If the LLM just wanted to chat normally without calling a tool
#         return {
#             "expense_results": response.content,
#             "messages": [response],
#             "llm_calls": state.get("llm_calls", 0) + 1
#         }   
        
# def itinerary_agent(state: TravelState):
#     """
#     Synthesizes the gathered flight, hotel, and weather data into a final, 
#     comprehensive travel itinerary for the user.
#     """
#     print("[Agent] Running Itinerary Agent...\n")
#     prompt = ITINERARY_PROMPT.format(
#         query=state['user_query'],
#         flight_results=state['flight_results'],
#         hotel_results=state['hotel_results'],
#         weather_results=state['weather_results']  
#     )

#     response = llm_reasoning.invoke([
#         SystemMessage(content="You are an expert travel planner"),
#         HumanMessage(content=prompt)
#     ])

#     return {
#         "itinerary": response.content,
#         "messages": [response],
#         "llm_calls": state.get("llm_calls", 0) + 1
#     }

# def route_user_query(state: TravelState) -> str:
#     """
#     Uses an LLM with structured output to semantically classify user intent
#     and route to the correct starting node.
#     """
#     query = state['user_query']
    
#     # 1. Bind the Pydantic schema to your LLM
#     structured_router = llm_tool.with_structured_output(RouterDecision)
    
#     # 2. System prompt guiding the classification
#     system_prompt = (
#         "You are an expert routing classifier for a Travel & Expense system. "
#         "Analyze the user's input and determine whether their primary goal is: "
#         "1. Logging, managing, or querying money/expenses -> 'expense_agent'\n"
#         "2. Planning a journey, booking flights, hotels, or viewing an itinerary -> 'flight_agent'"
#     )
    
#     try:
#         decision: RouterDecision = structured_router.invoke([
#             SystemMessage(content=system_prompt),
#             HumanMessage(content=f"User Query: {query}")
#         ])
#         print(f"-> [Router] LLM selected route: {decision.next_node}")
#         return decision.next_node
#     except Exception as e:
#         print(f"-> [Router] Fallback triggered due to error: {e}")
#         # Safe fallback in case of an API issue
#         return "flight_agent"

# ==========================================
# 5. GRAPH CONSTRUCTION
# ==========================================
# def build_travel_graph():
#     """
#     Initializes the LangGraph state graph, adds all agent nodes, 
#     and defines the execution edges (workflow path).
#     """
#     graph = StateGraph(TravelState)

#     # Add Nodes
#     graph.add_node("flight_agent", flight_agent)
#     graph.add_node("hotel_agent", hotel_agent)
#     graph.add_node("weather_agent", weather_agent)  
#     graph.add_node("expense_agent",expense_agent)
#     graph.add_node("itinerary_agent", itinerary_agent)

#     # Define Edges (Workflow flow)
#     graph.add_conditional_edges(START, route_user_query,
#         {
#             "expense_agent": "expense_agent",
#             "flight_agent": "flight_agent"
#         }
#     )
#     graph.add_edge("expense_agent",END)
#     graph.add_edge("flight_agent", "hotel_agent")
#     graph.add_edge("hotel_agent", "weather_agent")
#     graph.add_edge("weather_agent", "itinerary_agent")
#     graph.add_edge("itinerary_agent", END)
    
#     return graph

# def get_compiled_app():
#     """
#     Initializes the Database and returns the compiled app globally for Streamlit.
#     """
#     os.makedirs("data", exist_ok=True)
#     conn = sqlite3.connect("data/agents.db", check_same_thread=False)
#     checkpointer = SqliteSaver(conn)
    
#     graph = build_travel_graph()
#     return graph.compile(checkpointer=checkpointer)

# ==========================================
# 6. MAIN EXECUTION
# ==========================================
# def main():
#     """
#     Sets up the PostgreSQL checkpointer, compiles the graph, 
#     takes user input, and invokes the travel workflow.
#     """
#     # 1. Setup Database Connection & Checkpointer
#     # Handled locally here so it doesn't execute simply by importing the file
#     app = get_compiled_app()

#     # 3. Configure Thread Context for Memory
#     config = {
#         'configurable': {
#             'thread_id': 'user_sagar'
#         }
#     }

#     # 4. Get Input and Invoke Workflow
#     user_input = input("Enter travel request or Expense request: ")

#     result = app.invoke(
#         {
#             'messages': [HumanMessage(content=user_input)],
#             'user_query': user_input,
#             'flight_results': "",
#             'hotel_results': "",
#             'weather_results': "",
#             'expense_results': "",
#             'itinerary': "",
#             'llm_calls': 0
#         },
#         config=config
#     )

#     # 5. Display Final Result
#     print("\n====================================")
#     print("          FINAL RESPONSE            ")
#     print("====================================")
    
#     # We generally only want to print the final itinerary message 
#     # (the last item) rather than intermediate AIMessage logs.
#     for msg in result['messages']:
#         print(f"- {msg.content}")

# if __name__ == "__main__":
#     main()




"""CLI entry point for the Travel & Expense LangGraph app."""
from langchain_core.messages import HumanMessage

from src.graph import get_compiled_app


def main():
    """Compiles the graph, takes user input, and invokes the travel/expense workflow."""
    app = get_compiled_app()

    config = {"configurable": {"thread_id": "user_sagar"}}

    user_input = input("Enter travel request or Expense request: ")

    result = app.invoke(
        {
            "messages": [HumanMessage(content=user_input)],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "weather_results": "",
            "expense_results": "",
            "itinerary": "",
            "llm_calls": 0,
        },
        config=config,
    )

    print("\n====================================")
    print("          FINAL RESPONSE            ")
    print("====================================")

    # Only the final itinerary / expense message really matters to the user,
    # but we print everything here for debugging visibility.
    for msg in result["messages"]:
        print(f"- {msg.content}")


if __name__ == "__main__":
    main()
