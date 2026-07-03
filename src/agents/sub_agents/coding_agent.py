from google.adk.agents import Agent
from src.agents.prompts.coding_prompt import CODING_PROMPT

coding_agent = Agent(
    name="coding_agent",
    description="A specialist in software engineering, programming, refactoring, and code debugging. Use this agent whenever the user asks for code, programming concepts, or software help.",
    model="gemini-2.5-flash-lite",
    instruction=CODING_PROMPT,
    mode="single_turn",
)
