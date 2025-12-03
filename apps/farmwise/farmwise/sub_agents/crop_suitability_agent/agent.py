from google.adk.agents import Agent

from farmwise.tools.agronomy import soil_properties

from .prompt import crop_suitability_agent_instructions

crop_suitability_agent = Agent(
    name="crop_suitability_agent",
    description="A helpful agent that can answer questions about crop suitability.",
    instruction=crop_suitability_agent_instructions,
    tools=[
        # suitability_index,
        soil_properties
    ],
    model="gemini-2.5-flash",
)
