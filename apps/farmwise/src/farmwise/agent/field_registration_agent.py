from agents import Agent, RunContextWrapper
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

from farmwise.context import UserContext
from farmwise.schema import TextResponse
from farmwise.tools.farmbase import update_contact


def farm_registration_agent_instructions(ctx: RunContextWrapper[UserContext], agent: Agent[UserContext]) -> str:
    return f"""{RECOMMENDED_PROMPT_PREFIX}

1  Role

You register farms (fields) in the Farmbase database through a WhatsApp chat with the user.
For each field you must capture and save:
	1.	field_name – the name the farmer uses.
	2.	boundary – a sequence of GPS points supplied via WhatsApp’s location-sharing while the user walks the perimeter 
        (a closed polygon).
	3.	planting_intention – the crop the user plans to plant.
	4.	planting_date – the planned or actual planting date (YYYY-MM-DD).

When all required details for a field are confirmed, call the tool create_field exactly once with the JSON schema shown
below, then ask whether the user has another field.
After the last field is stored, send the single line ##FARM_REGISTRATION_COMPLETE## and stop replying.

These are the details of the current user: {ctx.context}


"""


farm_registration_agent: Agent[UserContext] = Agent(
    name="Field Registration Agent",
    handoff_description="This agent is used for registering a field in the system",
    instructions=farm_registration_agent_instructions,
    tools=[update_contact],
    output_type=TextResponse,
    model="gpt-4.1",
)
