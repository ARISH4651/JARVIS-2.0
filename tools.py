import logging
from livekit.agents import function_tool , RunContext
import requests
from langchain_community.tools import DuckDuckGoSearchRun

@function_tool()
async def get_weather(
    context: RunContext,
    city: str)->str:
    """Get the current weather for a given city using wttr.in API."""
    try:
        response = requests.get(f"https://wttr.in/{city}?format=3")
        if response.status_code == 200:
            logging.info(f"Weather for {city}: {response.text.strip()}")
            return response.text.strip()
        else:
            logging.error(f"Failed to fetch weather for {city}: {response.status_code}")
            return f"Could not retrieve weather data for {city}."
    except Exception as e:
        logging.error(f"Error fetching weather for {city}: {e}")
        return f"An error occurred while fetching the weather {city}."
    
@function_tool()
async def web_search(
    context: RunContext,
    query: str)->str:
    """Perform a web search using DuckDuckGo."""
    try:
        results = DuckDuckGoSearchRun().run(tool_input=query)
        logging.info(f"Search results for '{query}': {results}")
        return results
    except Exception as e:
        logging.error(f"Error performing web search for '{query}': {e}")
        return f"An error occurred while performing the web search for '{query}'."