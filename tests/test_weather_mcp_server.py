import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

client = MultiServerMCPClient(
    {
        "weather":{
            "transport":"stdio",
            "command":r"E:\TP-3\.venv\Scripts\python.exe",
            "args":[
                r"E:\TP-3\openweather-mcp\weather_mcp_server.py"
            ],
            "env": {
               "OPENWEATHER_API_KEY": OPENWEATHER_API_KEY 
            }
        }
    }
)

async def main():
    tools = await client.get_tools()
    print("\nAvailable MCP Tools:\n")
    for tool in tools:
        print(tool.name)


if __name__=="__main__":
    asyncio.run(main())


