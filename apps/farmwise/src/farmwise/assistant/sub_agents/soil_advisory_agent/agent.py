from google.adk.agents import Agent

from farmwise.tools.tools import soil_properties

from .prompt import soil_advisory_instructions

soil_advisor_agent = Agent(
    name="soil_advisor",
    description="An agent that can advises on soil management for farmers",
    instruction=soil_advisory_instructions,
    tools=[soil_properties],
    model="gemini-2.5-flash",
)
