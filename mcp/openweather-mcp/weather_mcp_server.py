# ==========================================
# 1. IMPORTS
# ==========================================
import os
import requests
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP

# ==========================================
# 2. CONFIGURATION & SETUP
# ==========================================
load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Initialize the FastMCP Server
mcp = FastMCP("weather_server")


# ==========================================
# 3. MCP TOOLS
# ==========================================
@mcp.tool()
def get_current_weather(city: str) -> dict:
    """
    Fetches the current weather conditions for a specified city using the OpenWeather API.
    Returns parsed metrics including temperature, humidity, wind speed, and general conditions.
    """
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
    )

    data = response.json()

    # Early return if the API call fails (e.g., invalid city or API key)
    if response.status_code != 200:
        return data

    return {
        "city": data["name"],
        "temperature_c": data["main"]["temp"],
        "feels_like_c": data["main"]["feels_like"],  # Fixed: API returns 'feels_like'
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"]
    }


@mcp.tool()
def get_forecast(city: str) -> dict:
    """
    Fetches a short-term weather forecast for a specified city using the OpenWeather API.
    Extracts and returns only the next 5 forecast time slots to keep the payload concise.
    """
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/forecast",
        params={
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
    )

    data = response.json()

    # Early return if the API call fails
    if response.status_code != 200:
        return data

    forecast = []

    # Iterate through the first 5 forecast entries (typically 3-hour intervals)
    for item in data["list"][:5]:
        forecast.append(
            {
                "datetime": item["dt_txt"],
                "temperature": item["main"]["temp"],
                "weather": item["weather"][0]["description"]
            }
        )

    return {
        "city": data["city"]["name"],  # Fixed: Forecast endpoint nests city name under 'city'
        "forecast": forecast
    }


# ==========================================
# 4. MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    # Start the MCP server using standard I/O for communication
    mcp.run()