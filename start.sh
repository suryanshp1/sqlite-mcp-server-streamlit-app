#!/bin/bash

# Wait for Ollama to be ready
echo "Waiting for Ollama to be ready..."
until curl -s http://ollama:11434/api/tags > /dev/null; do
    sleep 2
done

# Pull DeepSeek model if not exists
echo "Ensuring DeepSeek model is available..."
curl -X POST http://ollama:11434/api/pull -d '{"name": "llama3.2:1b"}'

# Start MCP server in background
echo "Starting MCP server..."
python src/mcp_server.py --server_type=sse &

# Wait a moment for MCP server to start
sleep 5

# Start Streamlit app for Ollama client
echo "Starting Streamlit Ollama client..."
streamlit run src/ollama_client.py --server.port 8501 --server.address 0.0.0.0
