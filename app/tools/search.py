from langchain_community.tools.tavily_search import TavilySearchResults
from app.core.config import settings

def get_search_tool():
    """
    Returns the Tavily Search tool.
    """
    if not settings.TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY is not set in the environment variables.")
    
    return TavilySearchResults(
        tavily_api_key=settings.TAVILY_API_KEY,
        max_results=3
    )
