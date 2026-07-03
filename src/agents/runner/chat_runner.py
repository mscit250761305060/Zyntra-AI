from google.adk.runners import Runner
from src.agents.main_agent.agent import zyntra_agent
from src.agents.sessions.session_manager import session_manager

# Runner configured specifically for simple stateless or non-persisting chat queries
chat_runner = Runner(
    agent=zyntra_agent,
    app_name="chat_service",
    session_service=session_manager.session_service,
    auto_create_session=False,
)
