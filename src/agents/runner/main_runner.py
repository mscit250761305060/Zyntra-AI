from google.adk.runners import Runner
from src.agents.main_agent.agent import zyntra_agent
from src.agents.sessions.session_manager import session_manager

# Main runner for the top-level orchestrator agent
main_runner = Runner(
    agent=zyntra_agent,
    app_name="main_orchestrator",
    session_service=session_manager.session_service,
    auto_create_session=True,
)
