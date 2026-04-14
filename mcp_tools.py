# ===========================================
# Author:      Sushant Kakkeri
# Title:       Senior Enterprise Software
#              Engineer
# Application: MCP Research Assistant
# Created:     April 2026
# Copyright:   © 2026 Sushant Kakkeri
#              All Rights Reserved
# ===========================================

# mcp_tools.py
from datetime import datetime
import requests


def web_search(query: str) -> str:
    """Search the web for current information"""

    # Try 1 - DuckDuckGo with time limit
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(
                query,
                max_results=3,
                region='us-en',
                safesearch='off',
                timelimit='m'))

        if results:
            formatted = []
            for r in results:
                formatted.append(
                    f"**{r['title']}**\n"
                    f"{r['body']}\n"
                    f"Source: {r['href']}")
            return "\n\n".join(formatted)

    except Exception:
        pass

    # Try 2 - DuckDuckGo without time limit
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(
                query,
                max_results=3,
                region='us-en'))

        if results:
            formatted = []
            for r in results:
                formatted.append(
                    f"**{r['title']}**\n"
                    f"{r['body']}\n"
                    f"Source: {r['href']}")
            return "\n\n".join(formatted)

    except Exception:
        pass

    # Try 3 - Wikipedia as fallback
    try:
        import wikipedia
        wikipedia.set_lang("en")
        search_results = wikipedia.search(
            query, results=5)

        if search_results:
            for result in search_results:
                try:
                    summary = wikipedia.summary(
                        result,
                        sentences=5,
                        auto_suggest=False)
                    page = wikipedia.page(
                        result,
                        auto_suggest=False)
                    return (
                        f"📖 From Wikipedia "
                        f"(web search "
                        f"unavailable):\n\n"
                        f"**{page.title}**\n\n"
                        f"{summary}\n\n"
                        f"Source: {page.url}")
                except Exception:
                    continue

    except Exception:
        pass

    # Last resort message
    return (
        f"🔍 Web search temporarily "
        f"unavailable for '{query}'.\n"
        f"Please try a more specific "
        f"search term or try again "
        f"in a moment.")


def get_weather(city: str) -> str:
    """Get current weather for any city"""
    try:
        city_clean = city.strip().replace(
            " ", "+")
        url = (
            f"https://wttr.in/"
            f"{city_clean}?format=j1")

        response = requests.get(
            url, timeout=5)
        data = response.json()

        current = data['current_condition'][0]
        temp_f = current['temp_F']
        temp_c = current['temp_C']
        desc = current[
            'weatherDesc'][0]['value']
        humidity = current['humidity']
        feels_f = current['FeelsLikeF']
        feels_c = current['FeelsLikeC']
        wind_mph = current['windspeedMiles']
        visibility = current['visibility']

        nearest = data.get(
            'nearest_area', [{}])[0]
        area = nearest.get(
            'areaName', [{}])[0].get(
            'value', city)
        country = nearest.get(
            'country', [{}])[0].get(
            'value', '')

        return (
            f"🌤️ Weather in "
            f"{area}, {country}:\n\n"
            f"🌡️ Temperature: "
            f"{temp_f}°F ({temp_c}°C)\n"
            f"🤔 Feels like: "
            f"{feels_f}°F ({feels_c}°C)\n"
            f"☁️ Condition: {desc}\n"
            f"💧 Humidity: {humidity}%\n"
            f"💨 Wind: {wind_mph} mph\n"
            f"👁️ Visibility: "
            f"{visibility} km\n"
            f"🕐 Updated: "
            f"{datetime.now().strftime('%I:%M %p')}"
        )

    except requests.Timeout:
        return (
            f"⏱️ Weather request timed "
            f"out for {city}. "
            f"Please try again.")

    except Exception as e:
        return (
            f"⚠️ Could not get weather "
            f"for {city}.\n"
            f"Error: {str(e)}")


def wikipedia_search(topic: str) -> str:
    """Search Wikipedia for information"""
    try:
        import wikipedia
        wikipedia.set_lang("en")

        # Step 1 - Search with exact match first
        search_results = wikipedia.search(
            f'"{topic}"', results=5)

        # Step 2 - Try without quotes if needed
        if not search_results:
            search_results = wikipedia.search(
                topic, results=5)

        if not search_results:
            return (
                f"No Wikipedia results "
                f"found for '{topic}'.\n"
                f"Please try a more "
                f"specific search term.")

        # Step 3 - Try each result
        for result in search_results:
            try:
                summary = wikipedia.summary(
                    result,
                    sentences=5,
                    auto_suggest=False)
                page = wikipedia.page(
                    result,
                    auto_suggest=False)
                return (
                    f"📖 Wikipedia: "
                    f"**{page.title}**\n\n"
                    f"{summary}\n\n"
                    f"Source: {page.url}")

            except wikipedia\
                    .DisambiguationError as e:
                try:
                    # Use first specific option
                    summary = wikipedia.summary(
                        e.options[0],
                        sentences=5,
                        auto_suggest=False)
                    page = wikipedia.page(
                        e.options[0],
                        auto_suggest=False)
                    return (
                        f"📖 Wikipedia: "
                        f"**{page.title}**\n\n"
                        f"{summary}\n\n"
                        f"Source: {page.url}\n\n"
                        f"💡 Related: "
                        f"{', '.join(e.options[1:4])}")
                except Exception:
                    continue

            except wikipedia.PageError:
                continue

            except Exception:
                continue

        return (
            f"⚠️ Could not load Wikipedia "
            f"for '{topic}'.\n"
            f"Try the full official name.\n"
            f"Example: "
            f"'SpaceX' → "
            f"'SpaceX aerospace company'")

    except Exception as e:
        return (
            f"Wikipedia error: {str(e)}")


def get_current_datetime() -> str:
    """Get current date and time"""
    now = datetime.now()
    return (
        f"📅 Current Date & Time:\n\n"
        f"📆 Date: "
        f"{now.strftime('%A, %B %d, %Y')}\n"
        f"🕐 Time: "
        f"{now.strftime('%I:%M:%S %p')}\n"
        f"📅 Day of Year: "
        f"{now.strftime('%j')}\n"
        f"📅 Week Number: "
        f"{now.strftime('%U')}\n"
        f"🌍 Timezone: Local System Time"
    )


# ─────────────────────────────
# MCP TOOL DEFINITIONS
# ─────────────────────────────
MCP_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description":
                "Search the web for "
                "current live information, "
                "recent news or anything "
                "not in documents. "
                "Use for current events, "
                "latest news, recent "
                "discoveries, or any "
                "real-time data. "
                "Do NOT use for questions "
                "about uploaded documents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description":
                            "Specific search "
                            "query. Be precise "
                            "for best results. "
                            "Example: "
                            "'SpaceX Starship "
                            "latest launch 2026'"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description":
                "Get current live weather "
                "for any city in the world. "
                "Use ONLY for weather, "
                "temperature or climate "
                "questions about a real "
                "location today. "
                "Do NOT use for historical "
                "or document weather info.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description":
                            "City name to get "
                            "weather for. "
                            "Example: "
                            "'San Antonio Texas'"
                            " or 'Houston Texas'"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "wikipedia_search",
            "description":
                "Search Wikipedia for "
                "general knowledge about "
                "any topic, person, place "
                "or concept. "
                "Use for background info, "
                "definitions or explanations "
                "of well known topics. "
                "Always use the full "
                "official name for best "
                "results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description":
                            "Full official name "
                            "of topic to search. "
                            "Use complete names. "
                            "Example: "
                            "'SpaceX aerospace "
                            "company' or "
                            "'International "
                            "Space Station NASA'"
                    }
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description":
                "Get the current date "
                "and time right now. "
                "Use when user asks "
                "what time or date "
                "it is today.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


def execute_tool(tool_name: str,
                 tool_args: dict) -> str:
    """
    Execute a tool by name and
    return the result to the AI
    """
    tools = {
        "web_search": web_search,
        "get_weather": get_weather,
        "wikipedia_search": wikipedia_search,
        "get_current_datetime":
            get_current_datetime
    }

    if tool_name in tools:
        try:
            return tools[tool_name](
                **tool_args)
        except Exception as e:
            return (
                f"Tool '{tool_name}' "
                f"encountered an error: "
                f"{str(e)}\n"
                f"Please try again with "
                f"a different query.")

    return (
        f"Unknown tool: {tool_name}. "
        f"Available tools: "
        f"{', '.join(tools.keys())}")