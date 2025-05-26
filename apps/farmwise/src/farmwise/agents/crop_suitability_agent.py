from agents import Agent, RunContextWrapper
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from farmwise_schema.schema import WhatsAppResponse

from farmwise.dependencies import UserContext
from farmwise.tools.farmbase import update_contact
from farmwise.tools.tools import suitability_index


def crop_suitability_agent_instructions(ctx: RunContextWrapper[UserContext], agent: Agent[UserContext]) -> str:
    return f"""{RECOMMENDED_PROMPT_PREFIX}
You are an agent that gives advice on which agricultural crops are most suitable for a given area.
specific locations in Kenya.

# Routine
1. Request the farmer shares their location, unless it is already known. Add the action "location_request" to get the location
2. Use the suitability_index tool to obtain suitability index values for crops between 0-10000 from FAO GAEZ data. 10000 indicates high suitability, 0 indicates low suitability.
3. Present the top 5 choices as a list, and offer to give advice on growing these crops.

If the farmer asks a question that is not related to the routine, or when the routine is complete, transfer back to the triage agent.

These are the details of the current user: {ctx.context}
"""


crop_suitability_agent: Agent[UserContext] = Agent(
    name="Crop Suitability Agent",
    handoff_description="A helpful agent that can answer questions about crop suitability.",
    instructions=crop_suitability_agent_instructions,
    tools=[suitability_index, update_contact],
    output_type=WhatsAppResponse,
    model="gpt-4.1",
)
