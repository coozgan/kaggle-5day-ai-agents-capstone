# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**Jarbest** is an accessible AI personal companion built with Google's Agent Development Kit (ADK). It uses a multi-agent architecture to help users—especially those with visual or physical impairments—manage finances and purchases through a unified conversational interface.

## Architecture

The system follows a **hierarchical agent pattern** with specialized sub-agents:

### Root Agent (personal_agent/agent.py)
- **Orchestrator**: Central "Jarbest" agent that handles user requests and delegates to specialized agents
- **Memory-Enabled**: Uses `InMemoryMemoryService` and `InMemorySessionService` for contextual conversations
- **Auto-Save Callback**: Automatically persists session state after each turn via `auto_save_to_memory`
- **Key Features**: Accessibility-first responses, scam prevention, balance verification before purchases

### Finance Agent (Agent-as-Tool)
- Handles banking operations via **MCP (Model Context Protocol)**
- Connects to the Bank MCP Server using `MCPToolset` with `StreamableHTTPConnectionParams`
- Tools: `check_balance`, `send_money`

### Purchaser Agent (Agent-as-Tool)
- Delegates shopping requests to external vendor agents via **A2A (Agent-to-Agent) Protocol**
- Uses `RemoteA2aAgent` to proxy requests to Pizza and E-commerce agents
- Each remote agent exposes an agent card at `/.well-known/agent-card.json`

### Simulated External Services
- **Bank MCP** (`simulated_environment/bank_mcp/server.py`): FastMCP server with banking tools
- **Pizza Agent** (`simulated_environment/pizza_shop_agent/`): A2A-compatible agent for pizza orders
- **Ecommerce Agent** (`simulated_environment/ecommerce_agent/`): A2A-compatible agent for product searches/orders

## Key Technologies

- **Google ADK**: `google-adk[a2a,memory]` for agent framework
- **FastMCP**: For building MCP servers (bank)
- **A2A SDK**: For agent-to-agent communication
- **Gemini Models**: Default models include `gemini-2.5-flash` and `gemini-3-pro-preview`
- **Python 3.11+**: Required runtime
- **uv**: Package manager used for dependency management

## Development Commands

### Local Development (Docker Compose)
```bash
# Start all services locally
docker-compose up --build

# Access services:
# - Personal Agent UI: http://localhost:8080
# - Bank MCP: http://localhost:8888
# - Pizza Agent: http://localhost:10000
# - Ecommerce Agent: http://localhost:11000
```

### Running Individual Agents Locally
```bash
# Install dependencies
uv pip install --system .

# Run Bank MCP Server
python simulated_environment/bank_mcp/server.py

# Run Pizza Agent
python simulated_environment/pizza_shop_agent/pizza_shop/agent.py

# Run Ecommerce Agent
python simulated_environment/ecommerce_agent/ecommerce_agent/agent.py

# Run Personal Agent with ADK Web UI
adk web --host 0.0.0.0 --verbose --port 8080
```

### Cloud Deployment
```bash
# Deploy all services to Google Cloud Run
chmod +x deploy.sh
./deploy.sh

# Prerequisites: gcloud CLI, Docker, authenticated GCP project
```

## Environment Configuration

### Required Environment Variables

Create `personal_agent/.env` based on `.env_example`:

```bash
GOOGLE_GENAI_USE_VERTEXAI=0  # Use Gemini API (1 for Vertex AI)
GOOGLE_API_KEY=              # Your Google AI Studio API key
MODEL=gemini-2.5-flash       # Model to use
BANK_USER_ID=acc_12345       # User's bank account ID
BANK_MCP_URL=http://localhost:8888
PIZZA_AGENT_URL=http://localhost:10000
ECOMMERCE_AGENT_URL=http://localhost:11000
```

### A2A Agent Configuration (Critical)

When deploying A2A agents to Cloud Run, **MUST** set:
- `A2A_HOST`: Cloud Run service domain (e.g., `jarbest-pizza-agent-xyz.a.run.app`)
- `A2A_PROTOCOL`: `https` for Cloud Run, `http` for local
- `A2A_PORT`: Override port in agent card if needed (defaults to `PORT`)

## Code Patterns

### Creating MCP Tools
```python
from fastmcp import FastMCP

mcp = FastMCP("Service Name")

@mcp.tool()
def tool_name(param: str) -> str:
    """Tool description for the agent."""
    return result
```

### Creating A2A Agents
```python
from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

agent = Agent(
    model="gemini-2.5-flash",
    name="agent_name",
    description="What this agent does",
    instruction="System prompt",
    tools=[tool_functions]
)

# Convert to A2A-compatible FastAPI app
a2a_app = to_a2a(agent, host=host, port=port, protocol=protocol)
```

### Using Remote A2A Agents
```python
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

remote_agent = RemoteA2aAgent(
    name="agent_name",
    agent_card="https://service.url/.well-known/agent-card.json",
    description="What this agent provides"
)
```

### Memory Management
```python
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService
from google.adk.tools import load_memory

# Include load_memory tool in agent
agent = Agent(
    tools=[load_memory],
    after_agent_callback=auto_save_to_memory
)
```

## Important Notes

### Retry Configuration
All agents use HTTP retry logic for Gemini API calls:
```python
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)
```

### Accessibility Requirements
- Responses must be descriptive (suitable for text-to-speech)
- Avoid ASCII art or complex formatting
- Always state prices and totals explicitly
- Warn users about suspicious transactions

### Service Discovery
- Personal Agent expects environment variables for service URLs
- A2A agents autodiscover capabilities via agent cards
- MCP tools are loaded dynamically via `MCPToolset`

## Project Structure
```
adk01/
├── personal_agent/          # Main orchestrator agent
│   ├── agent.py            # Root agent with memory and tool delegation
│   └── .env_example        # Environment template
├── simulated_environment/   # External services (for demo)
│   ├── bank_mcp/           # MCP banking server
│   ├── pizza_shop_agent/   # A2A pizza agent
│   └── ecommerce_agent/    # A2A ecommerce agent
├── deploy.sh               # Cloud Run deployment script
├── docker-compose.yml      # Local multi-service setup
└── Dockerfile             # Unified container image
```

## Testing the System

1. **Check Balance**: "What's my bank balance?"
2. **Order Pizza**: "Order a pepperoni pizza"
3. **Safe Purchase**: "Order a pizza if I can afford it"
4. **Search Products**: "Find a gaming laptop"
5. **Memory Recall**: "Order my usual" (after establishing preference)
