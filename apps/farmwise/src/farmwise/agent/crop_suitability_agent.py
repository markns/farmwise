from agents import Agent, RunContextWrapper
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

from farmwise.agent.prompt_utils import get_profile_and_memories
from farmwise.context import UserContext
from farmwise.schema import TextResponse
from farmwise.tools.farmbase import update_contact
from farmwise.tools.tools import suitability_index, soil_properties


def crop_suitability_agent_instructions(ctx: RunContextWrapper[UserContext], agent: Agent[UserContext]) -> str:
    from farmwise.whatsapp.activities import activities
    return f"""{RECOMMENDED_PROMPT_PREFIX}
You are an agent that gives advice on which agricultural crops are most suitable for a given area.
specific locations in Kenya.

# Routine
1. Request the farmer shares their location, unless it is already known. Add the action "location_request" to get the 
location
2. Use the suitability_index tool to obtain suitability index values for crops between 0-10000 from FAO GAEZ data. 
10000 indicates high suitability, 0 indicates low suitability.
3. Present the top 5 choices as a list, and offer to give advice on growing these crops.

If the farmer asks a question that is not related to the routine, transfer back to the triage agent.
 
When the interaction is complete prompt the user to ask follow up questions, and add the following section list 
to the response to offer the user a new list of activities: {activities}

{get_profile_and_memories(ctx.context)}
"""


crop_suitability_agent: Agent[UserContext] = Agent(
    name="Crop Suitability Agent",
    handoff_description="A helpful agent that can answer questions about crop suitability.",
    instructions=crop_suitability_agent_instructions,
    tools=[suitability_index, update_contact, soil_properties],
    output_type=TextResponse,
    model="gpt-4.1",
)
