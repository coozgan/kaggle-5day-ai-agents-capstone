from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.genai import types
import logging
import os
from dotenv import load_dotenv

load_dotenv()
gemini_model = os.getenv('MODEL')

logger = logging.getLogger(__name__)

# Configure Retry Options
retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)

# --- Tools ---

# Mock Database
MOCK_DB = {
    "inventory": {
        "gaming laptop": {"price": 1500, "stock": 5},
        "wireless headphones": {"price": 200, "stock": 15},
        "smart watch": {"price": 300, "stock": 10},
        "4k monitor": {"price": 450, "stock": 8},
        "mechanical keyboard": {"price": 120, "stock": 20},
        "usb-c hub": {"price": 40, "stock": 50}
    }
}

def search_items(query: str) -> dict:
    """Searches for items in the mock inventory.

    Args:
        query: The item name to search for (e.g., 'pizza', 'laptop').

    Returns:
        Dictionary with status and list of matching items.
    """
    logger.info(f"Searching for item: {query}")
    results = {}
    for item_name, details in MOCK_DB["inventory"].items():
        if query.lower() in item_name.lower():
            results[item_name] = details
            
    if results:
        return {"status": "success", "items": results}
    else:
        return {"status": "error", "error_message": f"No items found matching '{query}'."}

def place_order(item_name: str, quantity: int) -> dict:
    """Places an order for an item.

    Args:
        item_name: The exact name of the item to order.
        quantity: The number of items to order.

    Returns:
        Dictionary with order status and total cost.
    """
    logger.info(f"Placing order: {quantity} x {item_name}")
    
    item = MOCK_DB["inventory"].get(item_name.lower())
    if not item:
        return {"status": "error", "error_message": f"Item '{item_name}' not available."}
    
    if item["stock"] < quantity:
        return {"status": "error", "error_message": f"Insufficient stock. Only {item['stock']} left."}
    
    total_cost = item["price"] * quantity
    
    # Simulate A2A communication (mock)
    logger.info(f"[A2A] Sending order request to External Vendor for {item_name}...")
    
    # Update mock inventory
    item["stock"] -= quantity
    
    return {
        "status": "success",
        "message": f"Order placed for {quantity} x {item_name}.",
        "total_cost": total_cost,
        "estimated_delivery": "45 mins"
    }

ecommerce_agent = Agent(
    model=Gemini(
        model=gemini_model,
        retry_options=retry_config
    ),
    name='ecommerce_agent',
    description='A helpful assistant for user questions.',
    instruction="""You are a purchasing agent. 
        Your goal is to help the user find and buy items.
        
        Rules:
        1. Always search for an item first to check price and availability.
        2. If the user wants to buy, use the place_order tool.
        3. Report the total cost and delivery time to the user.
        """,
        tools=[search_items, place_order]
)
# Make the agent A2A-compatible
# Make the agent A2A-compatible
port = int(os.getenv('PORT', 8080))
host = os.getenv('A2A_HOST', 'localhost')
# Allow explicit port override for A2A card (useful for port mapping/forwarding)
a2a_port = int(os.getenv('A2A_PORT', port))
protocol = os.getenv('A2A_PROTOCOL', 'http')
a2a_app = to_a2a(ecommerce_agent, host=host, port=a2a_port, protocol=protocol)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(a2a_app, host="0.0.0.0", port=port)