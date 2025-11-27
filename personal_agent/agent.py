from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.genai import types
from dotenv import load_dotenv
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import load_memory
from google.adk.runners import Runner

import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#  Load .env file
load_dotenv()
gemini_model = os.getenv('MODEL')

# Configure Retry Options
retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
)

# Initialize Memory Service

async def run_session(
    runner_instance: Runner, user_queries: list[str] | str, session_id: str = "default"
):
    """Helper function to run queries in a session and display responses."""
    print(f"\n### Session: {session_id}")

    # Create or retrieve session
    try:
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )
    except:
        session = await session_service.get_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )

    # Convert single query to list
    if isinstance(user_queries, str):
        user_queries = [user_queries]

    # Process each query
    for query in user_queries:
        print(f"\nUser > {query}")
        query_content = types.Content(role="user", parts=[types.Part(text=query)])

        # Stream agent response
        async for event in runner_instance.run_async(
            user_id=USER_ID, session_id=session.id, new_message=query_content
        ):
            if event.is_final_response() and event.content and event.content.parts:
                text = event.content.parts[0].text
                if text and text != "None":
                    print(f"Model: > {text}")


memory_service = (InMemoryMemoryService())  # ADK's built-in Memory Service for development and testing
# Create Session Service
session_service = InMemorySessionService()  # Handles conversations



# --- Constants ---
APP_NAME = "memory_example_app"
USER_ID = "mem_user"


# A2A Agents
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
# MCP Values
BANK_MCP_URL = os.getenv('BANK_MCP_URL')

## Helper Agents ##

# Finance Agent
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
                url=f"{BANK_MCP_URL.rstrip('/')}/mcp"
            )
        )
    ],
)

# Purchaser Agent
purchaser_agent = Agent(
    name="purchaser_agent",
    model=Gemini(
        model=gemini_model,
        retry_options=retry_config
    ),
    description="An agent that can help with purchasing operations like checking balances and sending money.",
    instruction=f"""You are a purchasing agent. 
        Your goal is to help the user find and buy items.
        
        Rules:
        1. Always search for an item first to check price and availability.
        2. If the user wants to buy, use the place_order tool.
        3. Report the total cost and delivery time to the user.
        """,
    tools=[
        AgentTool(pizza_agent_proxy), 
        AgentTool(ecommerce_agent_proxy)
        ],
)


async def auto_save_to_memory(callback_context):
    """Automatically save session to memory after each agent turn."""
    logger.info(f"Auto-saving session {callback_context._invocation_context.session.id} to memory.")
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session
    )

# Main Orchestrator Agent
root_agent = Agent(
    name='root_agent',
    model=Gemini(
        model=gemini_model,
        retry_options=retry_config
    ),
    description='You are Jarbest a helpful assistant for user questions.',
    instruction="""
    You are Jarbest, a helpful assistant.
    
    Your job is to act as an intermediary between the user and the tools (pizza_agent, finance_agent, ecommerce_agent).
    
    RULES:
    1. When the user asks a question, call the appropriate tool.
    2. When the tool returns a response, you MUST repeat that response to the user.
    3. DO NOT summarize if the tool asks a specific question. Repeat the question exactly.
    4. NEVER return an empty response. Always say something.
    5. Use the load_memory tool to recall past conversations if needed.
    """,
    tools=[
        AgentTool(finance_agent), 
        AgentTool(purchaser_agent),
        load_memory
        ],
    after_agent_callback=auto_save_to_memory
)

logger.info("Root Agent initialized.")