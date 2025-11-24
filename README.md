# Personal AI Agent Orchestrator - Capstone Project

This project demonstrates a sophisticated multi-agent system designed to act as a personal concierge, capable of managing finances and making purchases through a unified interface. Built as part of the **Kaggle 5-Day AI Agents Intensive**, this system leverages the Agent Development Kit (ADK), Model Context Protocol (MCP), and Agent-to-Agent (A2A) communication patterns.

## System Architecture

The following diagram illustrates the high-level workflow and interaction between the various agents in the system:

![Agent Architecture Diagram](agent_architecture.png)

## Workflow Description

The system is composed of a central orchestrator and specialized sub-agents, each handling specific domains of responsibility.

### 1. User Interface (Client)
- **Entry Point**: The user interacts with the system through a mobile or web client interface.
- **Client-to-Agent**: Requests are sent securely to the **Personal AI Agent** hosted on Google Cloud.

### 2. Personal AI Agent (Orchestrator)
- **Role**: Acts as the central brain of the system. It parses user intent and delegates tasks to the appropriate specialized agents.
- **Routing**: Depending on the request (e.g., "Check my balance" or "Order a pizza"), it routes instructions to either the Finance Agent or the Purchaser Agent.

### 3. Finance Agent (Agent as a Tool)
- **Role**: Manages all financial transactions and inquiries.
- **Capabilities**:
  - **Check Balance**: Retrieves current account status.
  - **Send Money**: Initiates transfers between accounts.
- **Integration**: Uses the **Model Context Protocol (MCP)** to securely communicate with the **Bank** system.

### 4. Purchaser Agent (Agent as a Tool)
- **Role**: Handles all procurement and shopping tasks.
- **Delegation**: It further delegates specific requests to domain-specific external agents using the **A2A (Agent-to-Agent) Protocol**.
  - **Pizza Order Agent**: For food delivery requests (e.g., `PLACE_ORDER`).
  - **E-Commerce Agent**: For general shopping and product searches (e.g., `SEARCH_ITEMS`).

## Key Technologies
- **Google Cloud**: Hosts the primary agent infrastructure.
- **Agent Development Kit (ADK)**: Framework for building the agents.
- **Model Context Protocol (MCP)**: Standardized protocol for connecting AI models to external data and tools (used for the Bank connection).
- **A2A Protocol**: Enables interoperability and communication between independent agents (used for Pizza and E-Commerce services).

## Project Track
**Concierge Agents**: This project fits the Concierge track by improving personal productivity through automated financial management and purchasing.
