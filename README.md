# 100% Local MCP Client

A fully local Model Context Protocol (MCP) client application that runs entirely without external dependencies, featuring a Streamlit UI, local LLM via Ollama, and SQLite-based data persistence.

## Features

- **100% Local Operation**: No external API calls or cloud dependencies
- **MCP Protocol Compliance**: Full support for tools, resources, and prompts
- **Local LLM**: llama3.2 served via Ollama
- **Persistent Storage**: SQLite database for conversations and knowledge
- **Context-Aware**: Maintains memory across sessions
- **Web UI**: Interactive Streamlit interface
- **Docker Support**: Easy deployment with Docker Compose
- **Multi-Client Support**: Compatible with Claude Desktop, Cursor, and other MCP clients

## Quick Start

1. **Clone the repository**:

```bash
git clone <repository-url>
cd 100-local-mcp-client
```

2. **Start with Docker Compose**:

```bash
2. **Start with Docker Compose**:
```


3. **Access the UI**:
- Streamlit UI: http://localhost:8501
- MCP Server: http://localhost:3001

## Configuration for External Clients

### Claude Desktop

Copy the configuration to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```bash
{
"mcpServers": {
    "100-local-mcp-client": {
        "command": "docker",
        "args": [
        "exec", "-i", "100-local-mcp-client-mcp-client-1",
        "python", "/app/src/mcp_server.py"
        ]
    }
    }
}
```


### Cursor IDE

1. Go to Settings → MCP → Add new global MCP server
2. Use the configuration from `config/cursor_config.json`

## Available Tools

- **add_data**: Store information in the local database
- **fetch_data**: Retrieve information with optional filtering  
- **get_memory_context**: Access conversation history and context

## Architecture

┌─────────────────┐ ┌──────────────────┐ ┌─────────────────┐
│ Streamlit UI │ │ MCP Client │ │ Local LLM │
│ │◄──►│ │◄──►│ (Llama3.2) │
└─────────────────┘ └──────────────────┘ └─────────────────┘
│
▼
┌──────────────────┐ ┌─────────────────┐
│ MCP Server │◄──►│ SQLite Database │
│ │ │ │
└──────────────────┘ └─────────────────┘


## Development

To run in development mode:

1. Install dependencies: `pip install -r requirements.txt`
2. Start Ollama: `ollama serve`
3. Pull model: `ollama pull llama3.2:1b`
4. Run MCP server: `python src/mcp_server.py`
5. Run Streamlit: `streamlit run src/streamlit_ui.py`

## License

MIT License
