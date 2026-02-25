# import asyncio
# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client
# from langchain_core.tools import StructuredTool
# from pydantic import BaseModel, Field

# # Configuration for your specific MCP server (e.g., a local database server)
# # You would typically load these from .env
# MCP_SERVER_COMMAND = "npx" 
# MCP_SERVER_ARGS = ["-y", "@modelcontextprotocol/server-filesystem", "./data"] # Example: filesystem server

# class MCPToolInput(BaseModel):
#     query: str = Field(description="The query or command to send to the MCP server tool")

# async def run_mcp_action(tool_name: str, arguments: dict):
#     """
#     Connects to an MCP server and executes a tool.
#     """
#     server_params = StdioServerParameters(
#         command=MCP_SERVER_COMMAND,
#         args=MCP_SERVER_ARGS,
#     )

#     async with stdio_client(server_params) as (read, write):
#         async with ClientSession(read, write) as session:
#             # Initialize connection
#             await session.initialize()
            
#             # List available tools (Optional: for debugging)
#             # tools = await session.list_tools()
            
#             # Call the specific tool exposed by the MCP server
#             result = await session.call_tool(tool_name, arguments)
#             return result.content

# def get_mcp_tool(mcp_tool_name="read_file"):
#     """
#     Wraps an MCP action into a LangChain tool.
#     """
#     # Wrapper function to bridge async MCP to sync LangChain (if needed) 
#     # or use Async tools directly.
#     def sync_wrapper(query: str):
#         # specific arguments depend on the MCP tool definition
#         return asyncio.run(run_mcp_action(mcp_tool_name, {"path": query}))

#     return StructuredTool.from_function(
#         func=sync_wrapper,
#         name="mcp_filesystem_agent",
#         description="Useful for accessing external files or systems connected via MCP. Use this to read live logs or external manuals.",
#         args_schema=MCPToolInput
#     )


import os
import asyncio
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 1. Input Schema
class ReadFileInput(BaseModel):
    file_path: str = Field(description="The relative path of the file to read (e.g., 'data/logs/service_log.txt').")

# 2. Function to Run MCP Client
async def run_mcp_read(file_path: str):
    # Get absolute path to project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    target_path = os.path.abspath(os.path.join(project_root, file_path))
    
    # Security check: Ensure we aren't reading outside the project
    if not target_path.startswith(project_root):
        return "Error: Access denied. File must be inside the project folder."

    # Server Parameters (This runs the Node.js server)
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", project_root],
        env=None
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Call the 'read_file' tool exposed by the Node.js server
                result = await session.call_tool("read_file", arguments={"path": target_path})
                
                if result.content and len(result.content) > 0:
                    return result.content[0].text
                return "File is empty."
    except Exception as e:
        return f"MCP Error: {str(e)}"

# 3. Synchronous Wrapper for LangChain
def read_local_file(file_path: str) -> str:
    """Wrapper to run the async MCP function synchronously."""
    return asyncio.run(run_mcp_read(file_path))

# 4. Export the Tool
def get_mcp_tool():
    return StructuredTool.from_function(
        func=read_local_file,
        name="read_local_file",
        description="Use this tool to read local log files. Provide the file path (e.g., 'data/logs/file.txt').",
        args_schema=ReadFileInput
    )
