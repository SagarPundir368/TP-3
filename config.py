import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_llm():
    llm_tools = ChatGroq(
    model="qwen/qwen3.6-27b", 
    temperature=0,
    api_key=GROQ_API_KEY
    )

    llm_reasoning = ChatGroq(
    model="openai/gpt-oss-120b", 
    temperature=0.7, # To Get creative writing in itineraries
    api_key=GROQ_API_KEY

    )
    return llm_tools,llm_reasoning