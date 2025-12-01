# Jarbest: The Accessible Personal Companion

**Jarbest** is an accessible personal agent designed to empower users—especially those with visual or physical impairments—to manage their digital lives with independence and security.

Built as part of the **Kaggle 5-Day AI Agents Intensive**, this project aligns with the **Agents for Good** track by solving a critical problem: the digital world is fragmented and often inaccessible.

## Problem Statement
For many users, especially the visually impaired, managing daily tasks involves navigating a maze of disjointed apps. Checking a bank balance, ordering food, and buying essentials requires switching contexts, dealing with inaccessible UIs, and risking security errors. A simple task like "Order dinner if I can afford it" becomes a complex, multi-step ordeal.

## The Solution: Jarbest
Jarbest unifies these fragmented services into a single, conversational interface. It acts as a trusted guardian, verifying financial health before every purchase and providing clear, descriptive feedback suitable for text-to-speech interaction.

## System Architecture

The following diagram illustrates the high-level workflow and interaction between the various agents in the system:

![Agent Architecture Diagram](agent_architecture.png)

## Workflow Description

The system is composed of a central orchestrator and specialized sub-agents, each handling specific domains of responsibility.

### 1. User Interface (Client)
- **Entry Point**: The user interacts with the system through a voice-enabled mobile or web client.
- **Client-to-Agent**: Requests are sent securely to the **Personal AI Agent** hosted on Google Cloud.

### 2. Personal AI Agent (Orchestrator)
- **Role**: Acts as the central brain and "eyes" of the system. It parses user intent and delegates tasks to the appropriate specialized agents.
- **Accessibility**: Optimized for clear, descriptive responses that work well with screen readers.
- **Safety**: Implements a "Guardian" protocol to verify transaction details and warn against suspicious activity.
- **Memory**: Equipped with **Memory Service** to store and recall user preferences (e.g., "usual pizza order") to reduce cognitive load.

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

## Memory & Persistence

The Personal AI Agent is enhanced with memory capabilities to provide a more personalized experience.

-   **Memory Service**: Utilizes `InMemoryMemoryService` to store user preferences and important information across different conversation sessions.
-   **Session Service**: Uses `InMemorySessionService` to manage active conversation contexts.
-   **Automatic Saving**: An `after_agent_callback` (`auto_save_to_memory`) is implemented to automatically persist the session state to memory after every agent turn.
-   **Retrieval**: The agent is equipped with the `load_memory` tool, allowing it to proactively search for and recall past interactions when needed.

*Note: The current implementation uses in-memory storage, which is volatile and resets when the application restarts.*

## Key Technologies
- **Google Cloud**: Hosts the primary agent infrastructure.
- **Agent Development Kit (ADK)**: Framework for building the agents.
- **Model Context Protocol (MCP)**: Standardized protocol for connecting AI models to external data and tools (used for the Bank connection).
- **A2A Protocol**: Enables interoperability and communication between independent agents (used for Pizza and E-Commerce services).

## Project Track
**Agents for Good**: This project empowers users with disabilities by providing a secure, voice-ready interface for financial and lifestyle management.

## Deployment

This system is designed to be deployed on Google Cloud Run or run locally using Docker.

### Prerequisites

*   Google Cloud Project with billing enabled.
*   `gcloud` CLI installed and authenticated.
*   Docker and Docker Compose installed.
*   **Google API Key** from [Google AI Studio](https://aistudio.google.com/).

### Configuration

**Note:** This repository does not include sensitive configuration files (like `.env`) or API keys. You must set these up manually.

1.  **Environment Variables**: The system relies on `GOOGLE_API_KEY` for the Gemini models.
2.  **Service URLs**: When deploying, services need to know each other's URLs (handled automatically by `deploy.sh` for Cloud Run).

### 🚀 Cloud Run Deployment

We provide a specialized script to automate the deployment of all 4 services to Google Cloud Run.

1.  Set your API key:
    ```bash
    export GOOGLE_API_KEY='your-api-key-here'
    ```
2.  Run the deployment script:
    ```bash
    chmod +x deploy.sh
    ./deploy.sh
    ```

For detailed deployment instructions, including troubleshooting and architecture details, please refer to [DEPLOYMENT.md](DEPLOYMENT.md).

### 💻 Local Development

To run the entire system locally using Docker Compose:

1.  Navigate to `personal_agent/` and create a `.env` file based on `.env_example`:
    ```bash
    cp personal_agent/.env_example personal_agent/.env
    # Edit .env to add your GOOGLE_API_KEY
    ```
2.  Run the stack:
    ```bash
    docker-compose up --build
    ```
3.  Access the services:
    *   **Personal Agent UI**: [http://localhost:8080](http://localhost:8080)
    *   Bank MCP: [http://localhost:8888](http://localhost:8888)
    *   Pizza Agent: [http://localhost:10000](http://localhost:10000)
    *   Ecommerce Agent: [http://localhost:11000](http://localhost:11000)

