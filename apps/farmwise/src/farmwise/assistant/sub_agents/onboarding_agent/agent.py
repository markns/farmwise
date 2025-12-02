from google.adk.agents import Agent

from farmwise.assistant.tools.farmbetter import update_farmbetter_user

from .prompt import onboarding_agent_instructions

onboarding_agent = Agent(
    name="onboarding_agent",
    description="This agent is used for onboarding new users into the system",
    instruction=onboarding_agent_instructions,
    tools=[update_farmbetter_user],
    model="gemini-2.5-flash",
)
