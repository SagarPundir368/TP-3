import asyncio
import datetime
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from src.prompts import EXPENSE_AGENT_PROMPT
from src.mcp_client import get_mcp_tool
from src.frontend.utils import extract_destination
from src.state import TravelState
from src.llm import llm_tool


def expense_agent(state: TravelState, config: RunnableConfig):
    """
    Handles financial requests, logging expenses, or summarizing costs using the native Expense MCP.
    """
    print("[Agent] Running Expense Agent...\n")
    query = state['user_query']

    # 1. Extract the thread_id securely from the LangGraph config
    current_thread = config.get("configurable", {}).get("thread_id", "unknown_user")

    # 2. Pass both the query, thread_id and today's date to the prompt
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")

    prompt = EXPENSE_AGENT_PROMPT.format(
        query=query, 
        thread_id=current_thread,
        current_date=today_date
    )
    # 1. Fetch the NATIVE tools directly from the MCP Client
    mcp_add_tool = asyncio.run(get_mcp_tool("add_expense"))
    mcp_list_tool = asyncio.run(get_mcp_tool("list_expenses"))
    mcp_summarize_tool = asyncio.run(get_mcp_tool("summarize"))

    # 2. Bind the native tools to the LLM
    tools = [mcp_add_tool, mcp_list_tool, mcp_summarize_tool]
    llm_with_tools = llm_tool.bind_tools(tools)

    # 3. Invoke using the bound LLM
    response = llm_with_tools.invoke([
        SystemMessage(content="You are an expert travel finance manager. You MUST use the provided tools to save or retrieve data. DO NOT write raw SQL."),
        HumanMessage(content=prompt)
    ])

    # 4. Intercept and execute the tool call if the LLM made one
    if response.tool_calls:
        results = []
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            print(f"-> [System] LLM triggered tool: {tool_name}")

            def extract_clean_text(raw_res):
                # Check if it is a list and contains the 'text' key
                if isinstance(raw_res, list) and len(raw_res) > 0 and 'text' in raw_res[0]:
                    return raw_res[0]['text']
                return str(raw_res)
            
            # Execute the native MCP tools using their built-in ainvoke method
            if tool_name == "add_expense":
                raw_res = asyncio.run(mcp_add_tool.ainvoke(tool_args))
                clean_text = extract_clean_text(raw_res)
                results.append(f"✅ Successfully logged expense! Details:\n```json\n{clean_text}\n```")

            elif tool_name == "list_expenses":
                raw_res = asyncio.run(mcp_list_tool.ainvoke(tool_args))
                clean_text = extract_clean_text(raw_res)
                results.append(f"📊 Expense List:\n{clean_text}")
            
            elif tool_name == "summarize":
                raw_res = asyncio.run(mcp_summarize_tool.ainvoke(tool_args))
                clean_text = extract_clean_text(raw_res)
                results.append(f"💰 Expense Summary:\n{clean_text}")
        
        final_text = "\n\n".join(results)
        
        return {
            "expense_results": final_text,
            "messages": [AIMessage(content=final_text)],
            "llm_calls": state.get("llm_calls", 0) + 1
        }
        
    else:
        # If the LLM just wanted to chat normally without calling a tool
        return {
            "expense_results": response.content,
            "messages": [response],
            "llm_calls": state.get("llm_calls", 0) + 1
        }   
        
