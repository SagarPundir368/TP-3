import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

load_dotenv()

AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

client = MultiServerMCPClient(
    {
        "avaiationstack":{
            "transport":"stdio",
            "command":r"E:\TP-3\aviationstack-mcp\.venv\Scripts\python.exe",
            "args": [
                "-m",
                "aviationstack_mcp",
                "mcp",
                "run"
            ],
            "env":{
                "AVIATIONSTACK_API_KEY":AVIATIONSTACK_API_KEY
            }
        }
    }
)

async def main():
    tools = await client.get_tools()
    print("\nAvailable MCP Tools:\n")
    for tool in tools:
        print(tool.name)


asyncio.run(main())

