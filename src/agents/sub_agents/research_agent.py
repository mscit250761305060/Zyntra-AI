from google.adk.agents import Agent
from src.agents.prompts.research_prompt import RESEARCH_PROMPT

research_agent = Agent(
    name="research_agent",
    description="A specialist in research, structured search, analysis of complex topics, and summarizing external knowledge sources. Use this agent for deep information gathering and queries requiring analysis.",
    model="gemini-2.5-flash-lite",
    instruction=RESEARCH_PROMPT,
    mode="single_turn",
)
