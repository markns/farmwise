from agents import Agent, RunContextWrapper
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from pywa.types import SectionList, Section, SectionRow

from farmwise.agent.prompt_utils import get_profile_and_memories
from farmwise.context import UserContext
from farmwise.schema import TextResponse
from farmwise.tools.farmbase import update_contact
from farmwise.tools.tools import aez_classification, elevation, growing_period, maize_varieties, soil_properties


def maize_variety_selector_instructions(ctx: RunContextWrapper[UserContext], agent: Agent[UserContext]) -> str:
    # TODO: these diseases and pests can be loaded from a database
    diseases = SectionList(
        button_title="Select disease",
        sections=[
            Section(
                title="Diseases",
                rows=[
                    SectionRow(title="Maize lethal necrosis", callback_data="Maize lethal necrosis (MLN)"),
                    SectionRow(title="Grey leaf spot", callback_data="Grey leaf spot (GLS)"),
                    SectionRow(title="Northern leaf blight", callback_data="Northern (Turcicum) leaf blight (NCLB)"),
                    SectionRow(title="Common & southern rusts", callback_data="Common & southern rusts"),
                    SectionRow(title="Stalk and ear rots", callback_data="Stalk and ear rots"),
                    SectionRow(title="Maize streak virus", callback_data="Maize streak virus (MSV)"),
                    SectionRow(title="Downy mildew", callback_data="Downy mildew"),
                    SectionRow(title="Tar spot", callback_data="Tar spot"),
                ],
            )
        ],
    )

    pests = SectionList(
        button_title="Select pests",
        sections=[
            Section(
                title="Pests",
                rows=[
                    SectionRow(title="Fall armyworm", callback_data="Fall armyworm"),
                    SectionRow(title="Stem borers", callback_data="Stem borers"),
                    SectionRow(title="Cutworms & earworms", callback_data="Cutworms & earworms"),
                ],
            )
        ],
    )

    return f"""{RECOMMENDED_PROMPT_PREFIX} 
You are an expert in Maize agronomy. Your task is to recommend suitable varieties of Maize to farmers in Kenya.
Use concise and simple language as much as possible.

Follow this protocol:

1.	Profile the Growing Environment
1.1 Request the farmer shares the location of their farm, unless it is already provided. 
    Add the action "location_request" to get the location.
1.2 Determine altitude (metres above sea level) using the elevation tool.
1.3 Determine soil ph using the soil_properties tool.
1.4 Determine aez classification using the aez_classification tool.
1.5 Determine local growing-season length using the growing_period tool.

2.	Identify Biotic Stresses
2.1 Ask the farmer to list diseases they are concerned about, by adding this section_list in the response: {diseases}
2.2 Ask the farmer to list crop pests they are concerned about, by adding this section_list in the response: {pests}

3.	Use the maize_varieties tool to find suitable varieties using the altitude and growing season length
3.2 Present a list of the varieties highlighting those that are resistant to diseases and crop pests the farmer has 
    mentioned, and yield potential.
3.3 Offer to find availability of these varieties by including a section_list in the response with the variety names.

If the farmer asks a question that is not related to the routine, or when the routine is complete, transfer back to the
 triage agent.

{get_profile_and_memories(ctx.context)}
"""


maize_variety_selector: Agent[UserContext] = Agent(
    name="Maize Variety Selector",
    handoff_description="An agent that can recommend suitable varieties of Maize",
    instructions=maize_variety_selector_instructions,
    tools=[elevation, soil_properties, aez_classification, growing_period, maize_varieties, update_contact],
    output_type=TextResponse,
    model="gpt-4.1",
)
