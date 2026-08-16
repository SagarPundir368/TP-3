import os
from datetime import datetime
import streamlit as st
import sqlite3
from src.prompts import EXTRACT_DESTINATION
from src.llm import llm_tool

def save_travel_plan(user_query, thread_id, collected):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"travel_plan_{thread_id}.md"
    save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "outputs","travel_plans")
    os.makedirs(save_dir, exist_ok=True)

    file_content = f"""# Travel Plan
**Query:** {user_query}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**User ID:** {thread_id}

---

## ✈️ Flight Information
{collected['flight_results'] or 'N/A'}

## 🏨 Hotel Information
{collected['hotel_results'] or 'N/A'}

## 🗓️ Itinerary
{collected['itinerary'] or 'N/A'}

## 🧠 Final Travel Plan
{collected['final_response'] or 'N/A'}

---
*LLM Calls: {collected['llm_calls']}*
"""
    file_path = os.path.join(save_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_content)
        
    return file_content, filename


def get_session_total_expense(thread_id):
    """Calculates the total expenses for a specific session."""
    try:
        # Connect to your expenses database
        conn = sqlite3.connect("data/expenses.db")
        cursor = conn.cursor()
        
        # Sum all amounts tied to this specific thread_id
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE thread_id = ?", (thread_id,))
        total = cursor.fetchone()[0]
        
        conn.close()
        return total if total is not None else 0.0
    except Exception as e:
        print(f"Database error: {e}")
        return 0.0


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
    response = llm_tool.invoke(prompt)
    return response.content.strip()
