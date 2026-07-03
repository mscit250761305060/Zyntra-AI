from google.adk.runners import Runner
from src.agents.main_agent.agent import zyntra_agent
from src.agents.sessions.session_manager import session_manager

# Runner coupled strictly with session state and persistence handling
session_runner = Runner(
    agent=zyntra_agent,
    app_name="session_manager_service",
    session_service=session_manager.session_service,
    auto_create_session=True,
)
