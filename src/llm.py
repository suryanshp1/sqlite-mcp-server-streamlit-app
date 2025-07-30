from llama_index.tools.mcp import McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent, ToolCallResult, ToolCall
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.core.workflow import Context
import asyncio


llm = Ollama(model="llama3.2:1b", temperature=0.1, request_timeout=120, base_url="http://ollama:11434")
Settings.llm = llm


SYSTEM_PROMPT = """You are a helpful agent that interacts with a local SQLite database via MCP tools.
You have access to two tools: add_data and fetch_data.

When a user asks you to perform database operations:
1. First, execute the appropriate SQL query using the tools
2. Then, analyze the response from the tool
3. Finally, present the results in a clear, human-readable format

Important:
- Don't just show the JSON query - execute it and show the results
- For add_data operations, confirm if the operation was successful
- For fetch_data operations, format and display the returned data
- If there's an error, explain it clearly to the user

Example response format for add_data:
"I executed your query. The operation was successful." or "Error: [error message]"

Example response format for fetch_data:
"Here are the results:
[formatted data]"
"""


async def get_agent(tools: McpToolSpec):
    """
    Create an agent that can interact with the MCP tools.

    Args:
        tools: McpToolSpec containing the MCP tools to be used by the agent.

    Returns:
        An instance of FunctionAgent configured with the provided tools.
    """
    agent = FunctionAgent(
            name="Local SQLite MCP Agent",
            tools=tools,
            description="agent that interacts with a local SQLite database via MCP tools",
            system_prompt=SYSTEM_PROMPT,
            llm=llm,
            max_iterations=3
    )
    return agent

async def handle_user_message(
    message_content: str,
    agent: FunctionAgent,
    agent_context: Context,
    verbose: bool = False,
    callback=None
):
    """Handle a user message by processing it with the agent."""
    try:
        handler = agent.run(message_content, ctx=agent_context)
        tool_output = None
        
        async for result in handler.stream_events():
            if verbose:
                if isinstance(result, ToolCall):
                    verbose_msg = f"🛠️ Using tool: {result.tool_name}"
                    if callback:
                        callback(verbose_msg)
                elif isinstance(result, ToolCallResult):
                    tool_output = result.tool_output
                    verbose_msg = f"📝 Tool {result.tool_name} returned: {tool_output}"
                    if callback:
                        callback(verbose_msg)

        # Get the final response
        response = await handler
        
        # If we have tool output, include it in the response
        if tool_output:
            try:
                # Parse the tool output if it's JSON
                import json
                output_data = json.loads(tool_output)
                
                if "success" in output_data:
                    if output_data["success"]:
                        if "data" in output_data:
                            # Format fetch results
                            result_str = "\nResults:\n"
                            for row in output_data["data"]:
                                result_str += f"{row}\n"
                            return f"{response}\n{result_str}"
                        else:
                            # Format add/create results
                            return f"{response}\nOperation completed successfully: {output_data['message']}"
                    else:
                        return f"Error: {output_data['message']}"
            except:
                pass
                
        return str(response)
    except Exception as e:
        error_msg = f"Error in handle_user_message: {str(e)}"
        if callback:
            callback(f"❌ {error_msg}")
        raise