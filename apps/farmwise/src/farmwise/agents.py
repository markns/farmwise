from __future__ import annotations as _annotations

from agents import (
    Agent,
    RunContextWrapper,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from farmwise_schema.schema import AgentInfo, WhatsappResponse

from farmwise.context import UserContext
from farmwise.tools.farmbase import update_contact
from farmwise.tools.tools import (
    aez_classification,
    elevation,
    growing_period,
    maize_varieties,
    soil_property,
    suitability_index,
)

# TODO: Split into separate modules, as shown in openai-agents-python/examples/financial_research_agent
#
# faq_agent = Agent[UserContext](
#     name="FAQ Agent",
#     handoff_description="A helpful agent that can answer questions about the airline.",
#     instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
#     You are an FAQ agent. If you are speaking to a customer, you probably were transferred to from the triage agent.
#     Use the following routine to support the customer.
#     # Routine
#     1. Identify the last question asked by the customer.
#     2. Use the faq lookup tool to answer the question. Do not rely on your own knowledge.
#     3. If you cannot answer the question, transfer back to the triage agent.""",
#     tools=[faq_lookup_tool],
# )
#
# seat_booking_agent = Agent[UserContext](
#     name="Seat Booking Agent",
#     handoff_description="A helpful agent that can update a seat on a flight.",
#     instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
#     You are a seat booking agent. If you are speaking to a customer, you probably were transferred to from the triage agent.
#     Use the following routine to support the customer.
#     # Routine
#     1. Ask for their confirmation number.
#     2. Ask the customer what their desired seat number is.
#     3. Use the update seat tool to update the seat on the flight.
#     If the customer asks a question that is not related to the routine, transfer back to the triage agent. """,
#     tools=[update_seat],
# )

# onboarding_agent: Agent[UserContext] = Agent(
#     name="Onboarding Agent",
#     instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
#     You are an onboarding agent. If you are speaking to a customer, you probably were transferred to from the triage agent.
#     Use the following routine to support the customer.
#     # Routine
#     1. Ask for their confirmation number.
#     2. Ask the customer what their desired seat number is.
#     3. Use the update seat tool to update the seat on the flight.
#     If the customer asks a question that is not related to the routine, transfer back to the triage agent. """,
#     handoff_description="A helpful agent that onboards farmers into the FarmWise system.",
#     tools=[],
# )


#         ...     buttons=SectionList(
#         ...         button_title='Get user', sections=[
#         ...             Section(title='Users', rows=[
#         ...                 SectionRow(title='Get user', callback_data=UserData(id=123, name='david', admin=True))
#         ...             ])                              # Here ^^^ we use the UserData class as the callback data
#         ...         ]
#         ...     )


# TODO: Why is maize not showing in results?
# TODO:
#     3. Create a visualization that shows the most suitable crops for the area.


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
    output_type=WhatsappResponse,
    model="gpt-4.1",
)


crop_pathogen_diagnosis_agent: Agent[UserContext] = Agent(
    name="Crop pathogen diagnosis agent",
    handoff_description="An agent that can identify crop pests and diseases from an image",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    Routine for Crop Pest and Disease Diagnosis Agent
	1.	Accept Image Input
        You will receive a photo of a crop. Accept only clear images that include leaves, stems, fruits, or other affected parts of the plant. If the image is blurry or incomplete, ask the user to send a clearer one.
	2.	Confirm the Crop
        Attempt to identify the crop from the image. If uncertain, ask the user to confirm the crop type (e.g., maize, tomato, bean).
	3.	Scan for Visible Symptoms
        Examine the image for visible symptoms such as:
            •	Leaf spots, lesions, discolouration, yellowing
            •	Wilting, stunting, or distortion
            •	Holes, chewing damage, or tunnels
            •	Fungal growth, mould, or rust
            •	Insects or eggs on the plant
	4.	Match to Known Conditions
        Use your trained knowledge of plant pathology and entomology to match the observed symptoms to known:
        •	Pests (e.g., Fall Armyworm, Aphids, Thrips)
        •	Diseases (e.g., Maize Lethal Necrosis, Blight, Rust, Mildew)
	5.	Evaluate Likelihood
        Provide a diagnosis with a confidence level (e.g., “High confidence: Fall Armyworm” or “Low confidence: could be fungal leaf spot”).
	6.	Ask for More Context (if needed)
        If the diagnosis is unclear, ask the user for:
            •	A closer or different-angle photo
            •	Information on recent weather
            •	When symptoms started
            •	What inputs or chemicals have been applied
	7.	Provide Actionable Advice
        Offer clear next steps based on the likely diagnosis. This could include:
            •	Pest or disease name
            •	Recommended treatments (organic or chemical)
            •	Whether immediate action is needed
            •	Preventative tips for future
	8.	Warn About Uncertainty When Appropriate
        If the image does not provide enough information, explain that a field inspection or lab test may be necessary.
	9.	Log the Diagnosis
        Record the diagnosis and advice in a structured format for future reference (e.g., crop, issue, treatment recommended, date).

    If the farmer asks a question that is not related to the routine, or when the routine is complete, transfer back to the triage agent. 
""",
    output_type=WhatsappResponse,
    tools=[update_contact],
    model="gpt-4.1",
)


def maize_variety_selector_instructions(ctx: RunContextWrapper[UserContext], agent: Agent[UserContext]) -> str:
    return f"""{RECOMMENDED_PROMPT_PREFIX} 
        You are an expert in Maize agronomy. Your task is to recommend suitable varieties of Maize to farmers in Kenya.
        Use concise and simple language as much as possible.
        
        Follow this protocol:
        
        1.	Profile the Growing Environment
        1.1 Request the farmer shares their location. Add the action "location_request" to get the location.
        1.2 Determine altitude (metres above sea level) using the elevation tool.
        1.3 Determine soil ph using the soil_property tool.
        1.4 Determine aez classification using the aez_classification tool.
        1.5 Determine local growing-season length using the growing_period tool.
        
        2.	Identify Biotic Stresses
        2.1 Ask the farmer to list diseases they are concerned about, by adding this section_list in the response: SectionList(button_title='Select disease', sections=[Section(title='Diseases', rows=[SectionRow(title='Maize lethal necrosis', callback_data='Maize lethal necrosis (MLN)'), SectionRow(title='Grey leaf spot', callback_data='Grey leaf spot (GLS)'), SectionRow(title='Northern leaf blight', callback_data='Northern (Turcicum) leaf blight (NCLB)'), SectionRow(title='Common & southern rusts', callback_data='Common & southern rusts'), SectionRow(title='Stalk and ear rots', callback_data='Stalk and ear rots'), SectionRow(title='Maize streak virus', callback_data='Maize streak virus (MSV)'), SectionRow(title='Downy mildew', callback_data='Downy mildew'), SectionRow(title='Tar spot', callback_data='Tar spot')])])
        2.2 Ask the farmer to list crop pests they are concerned about, by adding this section_list in the response: SectionList(button_title='Select pests', sections=[Section(title='Pests', rows=[SectionRow(title='Fall armyworm', callback_data='Fall armyworm'), SectionRow(title='Stem borers', callback_data='Stem borers'), SectionRow(title='Cutworms & earworms', callback_data='Cutworms & earworms')])])
        
        3.	
        3.1 Use the maize_varieties tool to find suitable varieties using the altitude and growing season length
        3.2 Present a list of the varieties highlighting those that are resistant to diseases and crop pests the farmer has mentioned, and yield potential.
        3.3 Offer to find availability of these varieties by including a section_list in the response with the variety names.

        These are the details of the current user: {ctx.context}
        """
    # 2.4 Request and log average seasonal rainfall (mm) and drought-risk pattern.
    #         5.	Check Yield Potential and Stability
    #         5.1 Retrieve multi-location or regional on-farm trial data for shortlisted varieties.
    #         5.2 Prioritise varieties with higher mean yield and lower coefficient of variation.
    #
    #         6.	Verify Seed Quality, Availability and Cost
    #         6.1 Confirm that seed is certified and sourced from an accredited agro-dealer.
    #         6.2 Record seed price and royalty fees; calculate estimated gross margin per hectare.
    #
    #         7.	Confirm Regulatory Compliance
    #         7.1 Establish whether the variety is GMO, non-GMO or gene-edited.
    #         7.2 Reject any variety not authorised for cultivation in the user’s jurisdiction.
    #         7.3 Note any subsidies or relief-seed programmes that would alter cost or supply.
    #
    #         8.	Evaluate Post-Harvest and Handling Traits
    #         8.1 Inspect breeder data for kernel hardness, husk tightness and lodging resistance.
    #         8.2 Discard varieties lacking adequate protection against mould or aflatoxin.
    #
    #         9.	Recommend On-Farm Comparison
    #         9.1 Direct the user to plant the top two or three shortlisted varieties in adjacent plots under
    #             identical management.
    #         9.2 Instruct the user to score emergence, disease incidence, lodging and yield at harvest.
    #
    #         10.	Issue Adoption Decision and Review Schedule
    #         10.1 Select the highest-scoring variety for full-field planting in the next season; retain the runner-up as
    #             a contingency.
    #         10.2 Set an annual reminder for the user to repeat Steps 2-9 to account for new hybrids, evolving pests,
    #             and climate shifts.


maize_variety_selector: Agent[UserContext] = Agent(
    name="Maize Variety Selector",
    handoff_description="An agent that can recommend suitable varieties of Maize",
    instructions=maize_variety_selector_instructions,
    tools=[elevation, soil_property, aez_classification, growing_period, maize_varieties],
    output_type=WhatsappResponse,
    handoffs=[crop_suitability_agent, update_contact],
    model="gpt-4.1",
)


def triage_agent_instructions(ctx: RunContextWrapper[UserContext], agent: Agent[UserContext]) -> str:
    return f"""{RECOMMENDED_PROMPT_PREFIX} 
        You are a helpful triaging agent. You can use your tools to delegate questions to other appropriate agents.
        
        These are the details of the current user: {ctx.context}
        """


triage_agent: Agent[UserContext] = Agent(
    name="Triage Agent",
    handoff_description="A triage agent that can delegate a customer's request to the appropriate agent.",
    instructions=triage_agent_instructions,
    handoffs=[
        crop_suitability_agent,
        maize_variety_selector,
        crop_pathogen_diagnosis_agent,
        # handoff(agent=seat_booking_agent, on_handoff=on_seat_booking_handoff),
    ],
    tools=[update_contact],
    output_type=WhatsappResponse,
    model="gpt-4.1",
)

maize_variety_selector.handoffs.append(triage_agent)
crop_suitability_agent.handoffs.extend([triage_agent, maize_variety_selector])
crop_pathogen_diagnosis_agent.handoffs.append(triage_agent)

DEFAULT_AGENT = triage_agent.name

agents: dict[str, Agent] = {
    triage_agent.name: triage_agent,
    maize_variety_selector.name: maize_variety_selector,
    crop_suitability_agent.name: crop_suitability_agent,
    crop_pathogen_diagnosis_agent.name: crop_pathogen_diagnosis_agent,
}


def get_all_agent_info() -> list[AgentInfo]:
    return [AgentInfo(key=agent_id, description=agent.handoff_description) for agent_id, agent in agents.items()]
