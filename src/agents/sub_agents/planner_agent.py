from google.adk.agents import Agent
from src.agents.prompts.planner_prompt import PLANNER_PROMPT

planner_agent = Agent(
    name="planner_agent",
    description="A specialist in planning, task estimation, scheduling, organizing agendas, and outlining step-by-step project checklists. Use this agent for scheduling and planning tasks.",
    model="gemini-2.5-flash-lite",
    instruction=PLANNER_PROMPT,
    mode="single_turn",
)
