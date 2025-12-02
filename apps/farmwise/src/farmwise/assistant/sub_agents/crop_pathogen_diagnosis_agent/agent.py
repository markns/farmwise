from google.adk.agents import Agent

from farmwise.assistant.tools.farmbetter import record_problem

from .prompt import crop_pathogen_diagnosis_agent_instructions

crop_pathogen_diagnosis_agent = Agent(
    name="crop_pathogen_diagnosis_agent",
    description="An agent that can identify crop pests and diseases from an image",
    instruction=crop_pathogen_diagnosis_agent_instructions,
    tools=[
        record_problem,
        # available_courses
    ],
    model="gemini-2.5-pro",
)
