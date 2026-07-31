# ======================================================
# Imports
# ======================================================

import os
import asyncio
from dotenv import load_dotenv

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq

# Local prompt imports
from agents.prompts import EXTRACT_DESTINATION

# ==========================================
# 1. CONFIGURATION & ENVIRONMENT SETUP
# ==========================================
load_dotenv()

LLM_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Initialize the Groq LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=LLM_API_KEY
)

# Initialize the Multi-Server MCP Client
client = MultiServerMCPClient(
    {
        # REMOTE MCP SERVER
        "tavily": {
            "transport": "streamable_http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
        },
        # LOCAL MCP SERVER (Aviationstack)
        "aviationstack": {
            "transport": "stdio",
            "command": r"E:\TP-3\aviationstack-mcp\.venv\Scripts\python.exe",
            "args": [
                "-m",
                "aviationstack_mcp",
                "mcp",
                "run"
            ],
            "env": {
                "AVIATIONSTACK_API_KEY": AVIATIONSTACK_API_KEY
            }
        },
        # CUSTOM LOCAL MCP SERVER (Weather)
        "weather": {
            "transport": "stdio",
            "command": r"E:\TP-3\.venv\Scripts\python.exe",
            "args": [
                r"E:\TP-3\openweather-mcp\weather_mcp_server.py"
            ],
            "env": {
                "OPENWEATHER_API_KEY": OPENWEATHER_API_KEY 
            }
        }
    }
)

# ==========================================
# 2. TOOL MANAGEMENT (Centralized)
# ==========================================
# We use a single dictionary to cache all discovered tools for cleaner access.
_mcp_tools_cache = {}

async def initialize_tools():
    """
    Connects to the configured MCP servers, discovers all available tools,
    and caches them in a global dictionary for quick access across functions.
    """
    global _mcp_tools_cache
    
    # Skip if already initialized
    if _mcp_tools_cache:
        return

    tools = await client.get_tools()
    for tool in tools:
        _mcp_tools_cache[tool.name] = tool
        
    print("\n[System] MCP Tools Initialized Successfully.")

async def get_mcp_tool(tool_name: str):
    """
    Retrieves a specific tool from the cache by its name. 
    Initializes the tools if they haven't been loaded yet.
    """
    await initialize_tools()
    return _mcp_tools_cache.get(tool_name)


# ==========================================
# 3. LLM HELPER FUNCTIONS
# ==========================================
def extract_destination(query: str) -> str:
    """
    Uses the Groq LLM to extract only the destination city or country 
    from a natural language user query.
    """
    prompt = EXTRACT_DESTINATION.format(
        query=query
    )
    response = llm.invoke(prompt)
    return response.content.strip()


# ==========================================
# 4. DOMAIN: TAVILY SEARCH
# ==========================================
async def tavily_mcp_search(query: str):
    """
    Executes a general web search using the Tavily MCP tool based on the provided query.
    """
    tool = await get_mcp_tool("tavily_search")
    if not tool:
        return "Tavily search tool unavailable."
        
    result = await tool.ainvoke({"query": query})
    return result


# ==========================================
# 5. DOMAIN: AVIATION
# ==========================================
async def aviation_mcp_call(tool_name: str, tool_args: dict = None):
    """
    A generic caller for any aviation-related MCP tool. 
    Pass the specific tool name and its arguments to invoke it.
    """
    tool = await get_mcp_tool(tool_name)
    if not tool:
        return f"Aviation tool '{tool_name}' unavailable."

    result = await tool.ainvoke(tool_args or {})
    return result

async def get_airport():
    """
    Retrieves a list of airports using the Aviationstack MCP server.
    """
    tool = await get_mcp_tool("list_airports")
    if not tool:
        return "Airport tool unavailable."

    result = await tool.ainvoke({})
    return result

async def get_airlines():
    """
    Retrieves a list of airlines using the Aviationstack MCP server.
    """
    tool = await get_mcp_tool("list_airlines")
    if not tool:
        return "Airlines tool unavailable."

    result = await tool.ainvoke({})
    return result


# ==========================================
# 6. DOMAIN: WEATHER
# ==========================================
async def weather_mcp_search(city: str):
    """
    Fetches the current weather conditions for a specified city 
    using the custom Weather MCP server.
    """
    tool = await get_mcp_tool("get_current_weather")
    if not tool:
        return "Weather tool unavailable."
        
    return await tool.ainvoke({"city": city})

async def forecast_mcp_search(city: str):
    """
    Fetches the weather forecast for a specified city 
    using the custom Weather MCP server.
    """
    tool = await get_mcp_tool("get_forecast")
    if not tool:
        return "Forecast tool unavailable."
        
    return await tool.ainvoke({"city": city})


# ==========================================
# 7. MAIN EXECUTION
# ==========================================
async def main():
    """
    Main entry point of the script. Initializes tools and prints 
    out all available tools across the connected MCP servers.
    """
    await initialize_tools()
    
    print("\n--- Available MCP Tools ---")
    for tool_name in _mcp_tools_cache.keys():
        print(f"- {tool_name}")
        
    # Example usage uncommented for testing:
    # dest = extract_destination("I want to fly to Paris next week")
    # print(f"\nExtracted Destination: {dest}")
    # print(await weather_mcp_search(dest))

if __name__ == "__main__":
    asyncio.run(main())