from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents.llm_agent import Agent
from google.genai import types
from pydantic import BaseModel
import os
import dotenv
import uuid

dotenv.load_dotenv()
gemini_model = os.getenv('MODEL')

# Configure Retry Options
retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)

class OrderItem(BaseModel):
    name: str
    quantity: int
    price: int


class Order(BaseModel):
    order_id: str
    status: str
    order_items: list[OrderItem]

# pizza menu
def get_pizza_menu() -> str:
    """Get the pizza menu."""
    return """
    {
    "pepperoni": 15.00,
    "cheese": 12.00,
    "veggie": 14.00
    }
    """
def create_pizza_order(order_items: list[OrderItem]) -> str:
    """
    Creates a new pizza order with the given order items.

    Args:
        order_items: List of order items to be added to the order.

    Returns:
        str: A message indicating that the order has been created.
    """
    try:
        order_id = str(uuid.uuid4())
        order = Order(order_id=order_id, status="created", order_items=order_items)
        print("===")
        print(f"order created: {order}")
        print("===")
    except Exception as e:
        print(f"Error creating order: {e}")
        return f"Error creating order: {e}"
    return f"Order {order.model_dump()} has been created"


root_agent = Agent(
    model=gemini_model,
    name='pizza_agent',
    description="External vendor's pizza shop agent that provides product information and availability and allows you to create order for pizza.",
    instruction="""
    # INSTRUCTIONS
    You are a specialized assistant for a pizza shop.
    Your sole purpose is to answer questions about what is available on pizza menu and price also handle order creation.
    If the user asks about anything other than pizza menu or order creation, politely state that you cannot help with that topic and can only assist with pizza menu and order creation.
    Do not attempt to answer unrelated questions or use tools for other purposes.

    # CONTEXT

    Provided below is the available pizza menu and it's related price:
    - Margherita Pizza: $10
    - Pepperoni Pizza: $14
    - Hawaiian Pizza: $11
    - Veggie Pizza: $10
    - BBQ Chicken Pizza: $13

    # RULES

    - If user want to do something, you will be following this order:
        1. Always ensure the user already confirmed the order and total price. This confirmation may already given in the user query.
        2. Use `create_pizza_order` tool to create the order
        3. Finally, always provide response to the user about the detailed ordered items, price breakdown and total, and order ID

    - DO NOT make up menu or price, Always rely on the provided menu given to you as context.
    """,
    tools=[
        create_pizza_order
    ],
)

# Make the agent A2A-compatible
a2a_app = to_a2a(root_agent, port=10000)