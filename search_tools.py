import time
import os

import httpx
from dotenv import load_dotenv
from langchain_core.tools import tool


load_dotenv()

YOUCOM_SEARCH_URL = "https://ydc-index.io/v1/search"


def _search_youcom(query: str, count: int = 5) -> dict:
    """Send a search request to You.com and retry once if it fails."""

    api_key = os.getenv("YDC_API_KEY")

    if not api_key:
        raise ValueError("YDC_API_KEY was not found in the .env file.")

    last_error = None

    for attempt in range(2):
        try:
            response = httpx.post(
                YOUCOM_SEARCH_URL,
                headers={
                    "X-API-Key": api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "query": query,
                    "count": count,
                },
                timeout=20,
            )

            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as error:
            last_error = error

            if attempt == 0:
                time.sleep(1)

    raise RuntimeError(
        f"You.com search failed after 2 attempts: {last_error}"
    )


@tool
def web_search(query: str) -> str:
    """Search the web for current information about a company."""

    data = _search_youcom(query)

    web_results = data.get("results", {}).get("web", [])

    if not web_results:
        return "No web results found."

    formatted_results = []

    for result in web_results[:5]:
        formatted_results.append(
            f"Title: {result.get('title', 'N/A')}\n"
            f"Description: {result.get('description', 'N/A')}\n"
            f"URL: {result.get('url', 'N/A')}"
        )

    return "\n\n".join(formatted_results)


@tool
def news_search(query: str) -> str:
    """Search for recent news about a company."""

    data = _search_youcom(f"latest news about {query}")

    news_results = data.get("results", {}).get("news", [])

    if not news_results:
        return "No recent news results found."

    formatted_results = []

    for result in news_results[:5]:
        formatted_results.append(
            f"Title: {result.get('title', 'N/A')}\n"
            f"Description: {result.get('description', 'N/A')}\n"
            f"Published: {result.get('page_age', 'N/A')}\n"
            f"URL: {result.get('url', 'N/A')}"
        )

    return "\n\n".join(formatted_results)