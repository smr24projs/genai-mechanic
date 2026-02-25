# import os
# import json
# from dotenv import load_dotenv
# from langchain.tools import tool
# from langchain_community.tools.tavily_search import TavilySearchResults

# load_dotenv()

# # Initialize Tavily
# tavily_tool = TavilySearchResults(max_results=5)

# # @tool
# # def vehicle_web_search(query: str):
# #     """
# #     Search the web for real-time vehicle diagnostic data, TSBs, and forums.
# #     """
# #     try:
# #         results = tavily_tool.run(query)
# #         # CRITICAL FIX: Convert List to JSON String to satisfy Gemini's output requirements
# #         return json.dumps(results, ensure_ascii=False)
# #     except Exception as e:
# #         return json.dumps({"error": str(e)})


# @tool
# def vehicle_web_search(query: str):
#     try:
#         results = tavily_tool.run(query)
#         # CRITICAL FIX: Wrap the list in json.dumps()
#         return json.dumps(results, ensure_ascii=False)
#     except Exception as e:
#         return json.dumps({"error": str(e)})




# import os
# import json
# from dotenv import load_dotenv
# from langchain.tools import tool
# from langchain_community.tools.tavily_search import TavilySearchResults

# load_dotenv()

# # Initialize Tavily
# tavily_tool = TavilySearchResults(max_results=5)

# @tool
# def vehicle_web_search(query: str):
#     """
#     Search the web for real-time vehicle diagnostic data, TSBs, and forums.
#     Useful for finding common faults, recalls, and forum discussions.
#     """
#     try:
#         # Run the search
#         results = tavily_tool.run(query)
        
#         # CRITICAL FIX: Convert List to JSON String to prevent Agent crash
#         return json.dumps(results, ensure_ascii=False)
        
#     except Exception as e:
#         return json.dumps({"error": str(e)})




import os
import json
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

# Load API keys FIRST
load_dotenv()

# Initialize Tavily with limited results to prevent freezing
tavily_tool = TavilySearchResults(max_results=3)

@tool
def vehicle_web_search(query: str) -> str:
    """
    Search the web for real-time vehicle diagnostic data,
    technical service bulletins, and forum discussions.
    """
    try:
        print(f"DEBUG: Searching Tavily for: {query}")
        results = tavily_tool.run(query)

        # Handle case where results is already a string
        if isinstance(results, str):
            return results

        # Truncate each result to prevent agent memory overload
        clean_results = []
        for res in results:
            if isinstance(res, dict):
                clean_results.append({
                    "url": res.get("url", ""),
                    "content": res.get("content", "")[:500] + "..."
                })

        # CRITICAL: Must return a JSON string, NOT a list
        return json.dumps(clean_results, ensure_ascii=False)

    except Exception as e:
        # Always return a string, even on error
        return json.dumps({"error": str(e)})
