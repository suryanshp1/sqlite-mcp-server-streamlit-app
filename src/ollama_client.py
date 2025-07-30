import streamlit as st
import asyncio
import tracemalloc
from llama_index.tools.mcp import McpToolSpec, BasicMCPClient
from llama_index.core.workflow import Context
from llm import get_agent, handle_user_message
import traceback

# Enable tracemalloc for better error tracking
tracemalloc.start()

def ensure_event_loop():
    """Ensure we have a running event loop that's consistent"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop

class AsyncStreamlitHelper:
    """Helper class to manage async operations in Streamlit"""
    def __init__(self):
        self.loop = ensure_event_loop()

    def run_async(self, coro):
        """Run an async coroutine in the main event loop"""
        return self.loop.run_until_complete(coro)

async def initialize_mcp():
    """Initialize MCP client and agent"""
    mcp_client = BasicMCPClient("http://localhost:3001/sse")
    mcp_tool = McpToolSpec(client=mcp_client)
    tools = await mcp_tool.to_tool_list_async()
    agent = await get_agent(tools)
    return agent

async def process_message(user_input, agent, context, verbose=True, callback=None):
    result = await handle_user_message(user_input, agent, context, verbose=verbose, callback=callback)
    return result

async def initialize_mcp_and_context():
    agent = await initialize_mcp()
    context = Context(agent)
    return agent, context

def main():
    st.title("MCP Ollama local SQLite MCP Chat")
    
    # Initialize async helper
    if 'async_helper' not in st.session_state:
        st.session_state['async_helper'] = AsyncStreamlitHelper()
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    
    # Create a placeholder for verbose output
    verbose_placeholder = st.empty()
    
    def show_verbose(message):
        """Callback to show verbose output in Streamlit"""
        verbose_placeholder.markdown(message)
    
    # Initialize agent and context if not present
    if 'agent' not in st.session_state or 'context' not in st.session_state:
        try:
            agent, context = st.session_state['async_helper'].run_async(initialize_mcp_and_context())
            st.session_state['agent'] = agent
            st.session_state['context'] = context
        except Exception as e:
            st.error(f"Failed to initialize agent: {str(e)}")
            st.error(f"Traceback: {traceback.format_exc()}")
            return

    user_input = st.text_input("You:", key="user_input")
    if st.button("Send") and user_input:
        st.session_state['chat_history'].append(("You", user_input))
        with st.spinner("Agent is thinking..."):
            try:
                response = st.session_state['async_helper'].run_async(
                    process_message(
                        user_input, 
                        st.session_state['agent'], 
                        st.session_state['context'],
                        verbose=True,
                        callback=show_verbose
                    )
                )
                
                if response:
                    st.session_state['chat_history'].append(("Agent", response))
                else:
                    st.warning("No response from agent")
                    
            except Exception as e:
                st.error(f"Error processing message: {str(e)}")
                st.error(f"Traceback: {traceback.format_exc()}")
        
        verbose_placeholder.empty()  # Clear verbose output after completion
        st.rerun()

    # Display chat history
    for speaker, message in st.session_state['chat_history']:
        st.markdown(f"**{speaker}:** {message}")

if __name__ == "__main__":
    main()