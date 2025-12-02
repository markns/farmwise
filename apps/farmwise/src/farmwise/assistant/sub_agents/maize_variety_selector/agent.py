from google.adk.agents import Agent

from farmwise.tools.tools import aez_classification, elevation, growing_period, maize_varieties, soil_properties

from .prompt import maize_variety_selector_instructions

maize_variety_selector = Agent(
    name="maize_variety_selector",
    description="An agent that can recommend suitable varieties of Maize",
    instruction=maize_variety_selector_instructions,
    tools=[elevation, soil_properties, aez_classification, growing_period, maize_varieties],
    model="gemini-2.5-flash",
)
