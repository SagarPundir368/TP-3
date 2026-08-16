import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

client = MultiServerMCPClient(
    {
        "expense_track":{
                    "transport":"stdio",
                    "command": r"E:\TP-3\.venv\Scripts\python.exe",
                    "args": [
                        r"E:\TP-3\mcp\expensetracker-mcp\expense_mcp_server.py"
                    ]
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


