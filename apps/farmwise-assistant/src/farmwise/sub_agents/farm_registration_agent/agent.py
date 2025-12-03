from google.adk.agents import Agent

from .prompt import farm_registration_agent_instructions

farm_registration_agent = Agent(
    name="farm_registration_agent",
    description="This agent is used for registering a field in the system",
    instruction=farm_registration_agent_instructions,
    model="gemini-2.5-flash",
)
