import os
from datetime import datetime
import streamlit as st

def save_travel_plan(user_query, thread_id, collected):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"travel_plan_{timestamp}.md"
    save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "travel_plans")
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