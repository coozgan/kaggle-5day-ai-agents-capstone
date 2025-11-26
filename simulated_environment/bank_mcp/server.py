import logging
import os
import asyncio
from fastmcp import FastMCP
from typing import Dict, Any

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP("Bank MCP Server 🏦")

# Dummy Data for Proof of Concept
ACCOUNTS: Dict[str, Dict[str, Any]] = {
    "acc_12345": {"name": "Alice", "balance": 5000.00},
    "acc_67890": {"name": "Bob", "balance": 150.50},
    "acc_54321": {"name": "Charlie", "balance": 10000.00},
    "acc_99999": {"name": "David", "balance": 0.00}
}

@mcp.tool()
def list_accounts() -> str:
    """List all available accounts in the bank.

    Returns:
        A string listing account IDs and owner names.
    """
    logger.info("--- 🛠️ Tool: list_accounts called ---")
    result = "Available Accounts:\n"
    for acc_id, data in ACCOUNTS.items():
        result += f"- ID: {acc_id}, Name: {data['name']}\n"
    return result

@mcp.tool()
def check_balance(account_id: str) -> str:
    """Check the balance of a specific account.

    Args:
        account_id: The ID of the account to check.

    Returns:
        A string indicating the balance of the account, or an error message if the account is not found.
    """
    logger.info(f"--- 🛠️ Tool: check_balance called for account {account_id} ---")
    if account_id not in ACCOUNTS:
        return f"Error: Account {account_id} not found."
    return f"Account {account_id} balance: {ACCOUNTS[account_id]['balance']:.2f}"

@mcp.tool()
def send_money(
    sender_id: str,
    receiver_id: str,
    amount: float,
) -> str:
    """Send money from one account to another.

    Args:
        sender_id: The ID of the account sending money.
        receiver_id: The ID of the account receiving money.
        amount: The amount of money to send.

    Returns:
        A string indicating the result of the transaction, or an error message if the transaction fails.
    """
    logger.info(f"--- 🛠️ Tool: send_money called from {sender_id} to {receiver_id} for {amount:.2f} ---")
    if sender_id not in ACCOUNTS or receiver_id not in ACCOUNTS:
        return "Error: Invalid account IDs."
    if ACCOUNTS[sender_id]['balance'] < amount:
        return "Error: Insufficient balance."
    ACCOUNTS[sender_id]['balance'] -= amount
    ACCOUNTS[receiver_id]['balance'] += amount
    return f"Transaction successful: {amount:.2f} sent from {sender_id} to {receiver_id}"

if __name__ == "__main__":
    logger.info(f"🚀 MCP server started on port {os.getenv('PORT', 8080)}")
    # Could also use 'sse' transport, host="0.0.0.0" required for Cloud Run.
    asyncio.run(
        mcp.run_async(
            transport="http",
            host="127.0.0.1",
            port=os.getenv("PORT", 8080),
        )
    )
