import os
from google.adk.agents import Agent
from src.core.config import settings
from src.agents.tools.calculator_tool import calculator
from src.agents.sub_agents.coding_agent import coding_agent
from src.agents.sub_agents.planner_agent import planner_agent
from src.agents.sub_agents.research_agent import research_agent
from src.agents.sub_agents.summarizer_agent import summarizer_agent
from src.agents.sub_agents.rag_agent import rag_agent
from src.agents.sub_agents.web_search_agent import web_search_agent
from src.agents.prompts.system_prompt import SYSTEM_PROMPT

# Ensure GEMINI_API_KEY is available in os.environ for adk/genai
os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY

zyntra_agent = Agent(
    name="chatbot",
    model="gemini-3.1-flash-lite",
    instruction=SYSTEM_PROMPT,
    tools=[calculator],
    sub_agents=[coding_agent, planner_agent, research_agent, summarizer_agent, rag_agent, web_search_agent],
    mode="chat",
)
