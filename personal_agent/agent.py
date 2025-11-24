from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.genai import types
from dotenv import load_dotenv
import os

#  Load .env file
load_dotenv()
gemini_model = os.getenv('MODEL')
# Configure Retry Options
retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)

pizza_agent_proxy = RemoteA2aAgent(
    name="pizza_agent",
    agent_card=f"{os.getenv('PIZZA_AGENT_URL', 'http://localhost:10000').rstrip('/')}/.well-known/agent-card.json",
    description="Remote product catalog agent from external vendor that provides product information.",
)
ecommerce_agent_proxy = RemoteA2aAgent(
    name="ecommerce_agent",
    agent_card=f"{os.getenv('ECOMMERCE_AGENT_URL', 'http://localhost:11000').rstrip('/')}/.well-known/agent-card.json",
    description="Remote product catalog agent from external vendor that provides product information.",
)

finance_agent = Agent(
    name="finance_agent",
    model=Gemini(
        model=gemini_model,
        retry_options=retry_config
    ),
    description="An agent that can help with banking operations like checking balances and sending money.",
    instruction=f"""
    You are a specialized banking assistant.
    Your purpose is to help users with their banking needs using the available tools.
    
    Capabilities:
    - Check account balances using 'check_balance' of the bank account id: {os.getenv('BANK_USER_ID', 'acc_12345')}.
    - Transfer money between accounts using 'send_money' from bank account id: {os.getenv('BANK_USER_ID', 'acc_12345')} to another bank account id.

    If the user asks about anything other than banking, politely state that you can only assist with banking queries.
    """,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=f"{os.getenv('BANK_MCP_URL', 'http://localhost:8080').rstrip('/')}/mcp"
            )
        )
    ],
)

root_agent = Agent(
    name='root_agent',
    model=Gemini(
        model=gemini_model,
        retry_options=retry_config
    ),
    description='A helpful assistant for user questions.',
    instruction="""
    You are a helpful assistant.
    
    Your job is to act as an intermediary between the user and the tools (pizza_agent, finance_agent, ecommerce_agent).
    
    RULES:
    1. When the user asks a question, call the appropriate tool.
    2. When the tool returns a response, you MUST repeat that response to the user.
    3. DO NOT summarize if the tool asks a specific question. Repeat the question exactly.
    4. NEVER return an empty response. Always say something.
    """,
    tools=[AgentTool(finance_agent), AgentTool(pizza_agent_proxy), AgentTool(ecommerce_agent_proxy)]
)