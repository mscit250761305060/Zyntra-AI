from google.adk.runners import Runner
from google.adk.agents import Agent
from src.agents.sessions.session_manager import session_manager

def get_agent_runner(agent: Agent, app_name: str = "generic_agent", auto_create_session: bool = True) -> Runner:
    """
    Factory function to create a dedicated runner for any specific sub-agent.
    Useful for directly invoking specific agents without the orchestrator.
    """
    return Runner(
        agent=agent,
        app_name=app_name,
        session_service=session_manager.session_service,
        auto_create_session=auto_create_session,
    )
