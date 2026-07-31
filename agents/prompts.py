
FLIGHT_AGENT_PROMPT = """
    You are a travel flight expert.

    User Query:
    {query}

    Airport Information:
    {airport_data}

    Airline Information:
    {airline_data}

    Generate:
    1. LIkelry departure airport
    2. Likely arrival airport
    3. Airlines serving this route
    4. Typical flight duration
    5. Estimated airfare range
    6. Peak season pricing warning
    7. Booking advice

    Return concise travel guidance.
"""

EXTRACT_DESTINATION = """
    Extract only the destination city or country.

    Query:
    {query}

    Return only the destination name
"""

ITINERARY_PROMPT = """
    Create a travel itinerary,
    User Query:
    {query}

    Flight Results:
    {flight_results}

    Hotel Results:
    {hotel_results}

    Weather Information:
    {weather_results}
"""
