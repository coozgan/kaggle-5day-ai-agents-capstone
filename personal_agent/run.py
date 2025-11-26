import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai.types import Content, Part
from agent import root_agent

# --- Configuration ---
# Store sessions in a local .adk folder in the user's home directory
SESSIONS_DIR = Path(os.path.expanduser("~")) / ".adk" / "sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)
DB_FILE = SESSIONS_DIR / "personal_agent_sessions.db"
SESSION_URL = f"sqlite:///{DB_FILE}"

# You can change these to support multiple users
MY_USER_ID = "user_001"
MY_SESSION_ID = f"{MY_USER_ID}_session"

async def main():
    print("🤖 Initializing Personal Agent with Memory...")
    print(f"🗄️  Session database is at: {DB_FILE}")
    print("--------------------------------------------------")

    # Initialize the session service (this handles saving/loading memory)
    session_service = DatabaseSessionService(db_url=SESSION_URL)
    
    # Get or create a session for the user
    session = await session_service.get_session(
        app_name=root_agent.name, user_id=MY_USER_ID, session_id=MY_SESSION_ID
    )
    if session is None:
        print(f"No existing session found. Creating a new one: {MY_SESSION_ID}")
        session = await session_service.create_session(
            app_name=root_agent.name, user_id=MY_USER_ID, session_id=MY_SESSION_ID
        )
    print(f"✅ Session '{session.id}' is ready.")

    # Create the runner
    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name=root_agent.name
    )

    print("\nChat with your agent (type 'quit' to exit):")
    while True:
        try:
            query = input("You: ")
            if query.lower() in ["quit", "exit"]:
                print("🤖 Goodbye!")
                break
            
            print("Agent: ", end="", flush=True)

            # Run the agent
            async for event in runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=Content(parts=[Part(text=query)], role="user")
            ):
                if not event.content:
                    continue

                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        print(part.text, end="", flush=True)
                    elif event.author == "user" and hasattr(part, "function_response"):
                        # Optional: Print tool outputs for debugging
                        # print(f"\n[Tool: {part.function_response.name}]", end="")
                        pass
            
            print("\n")

        except (KeyboardInterrupt, EOFError):
            print("\n🤖 Goodbye!")
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Shutting down.")
