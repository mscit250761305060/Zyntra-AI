from google.adk.agents import Agent
from src.agents.prompts.summarizer_prompt import SUMMARIZER_PROMPT

summarizer_agent = Agent(
    name="summarizer_agent",
    description="A specialist in summarization, text extraction, highlighting core takeaways, and condensing long messages or articles. Use this agent whenever a user asks to summarize text.",
    model="gemini-2.5-flash-lite",
    instruction=SUMMARIZER_PROMPT,
    mode="single_turn",
)
