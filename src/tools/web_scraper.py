# from langchain_community.tools import DuckDuckGoSearchRun
# from langchain_core.tools import Tool

# def get_web_scraper_tool():
#     # wrapper allows the agent to call this function
#     search = DuckDuckGoSearchRun()
    
#     return Tool(
#         name="web_search",
#         func=search.invoke,  # Must be .invoke for newer LangChain versions
#         description="Useful for finding live information, recalls, and news on the web."
#     )


import os
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

# 1. Input Schema
class SearchInput(BaseModel):
    query: str = Field(description="The query to search for (e.g., '2019 Honda Civic oil capacity').")

# 2. Setup the Tavily Tool
def get_web_scraper_tool():
    """
    Returns the Tavily Search tool which is optimized for AI Agents.
    It returns accurate search results without rate limits.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("❌ Error: TAVILY_API_KEY not found in .env")

    # Initialize the tool
    # max_results=3 is enough for an agent and saves your quota
    search_tool = TavilySearchResults(
        max_results=3,
        description="Use this tool to find recalls, TSBs, specs, and common vehicle problems."
    )
    
    return search_tool


# import time
# import random
# from langchain_community.tools import DuckDuckGoSearchRun
# from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
# from langchain_core.tools import StructuredTool
# from pydantic import BaseModel, Field

# class SearchInput(BaseModel):
#     query: str = Field(description="The query to search for.")

# def search_with_retry(query: str):
#     """Executes a web search with retry logic."""
#     wrapper = DuckDuckGoSearchAPIWrapper(max_results=5)
#     search = DuckDuckGoSearchRun(api_wrapper=wrapper)
    
#     # Try 3 times before failing
#     max_retries = 3
#     for attempt in range(max_retries):
#         try:
#             # Wait a tiny bit to look like a human
#             time.sleep(random.uniform(1.0, 3.0))
#             return search.invoke(query)
#         except Exception as e:
#             # If rate limited, wait longer
#             if "202" in str(e) or "Ratelimit" in str(e):
#                 wait_time = 5 * (attempt + 1)
#                 print(f"⚠️ Rate Limit. Waiting {wait_time}s...")
#                 time.sleep(wait_time)
#             else:
#                 return f"Search failed: {str(e)}"

#     return "Error: Search service unavailable. Please try again later."

# def get_web_scraper_tool():
#     return StructuredTool.from_function(
#         func=search_with_retry,
#         name="web_search",
#         description="Search the web for recalls, common problems, and specs.",
#         args_schema=SearchInput
#     )
