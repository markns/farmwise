from __future__ import annotations as _annotations

from agents import (
    Agent,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from farmwise_schema.schema import AgentInfo, WhatsappResponse

from farmwise.context import UserContext
from farmwise.tools import aez_classification, elevation, growing_period, maize_varieties, soil_property

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


#
# crop_suitability_agent: Agent[UserContext] = Agent(
#     name="Crop Suitability Agent",
#     handoff_description="A helpful agent that can answer questions about crop suitability.",
#     instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
#     You are an agent that gives advice on which seed varieties of agricultural crops are suitable for growing in
#     specific locations in Kenya.
#
#     # Routine
#     1. Ask what type of crop the farmer wants to grow.
#     2. Ask the farmer what their location is, if it's not already provided. Add the action "location_request" to get the
#      location from the farmer.
#     3. Use the crop suitability tool to find the crop varieties that are suitable for the farmers location.
#
#     If the farmer asks a question that is not related to the routine, transfer back to the triage agent. """,
#     tools=[crop_suitability],
#     output_type=WhatsappResponse,
#     model="gpt-4.1-mini",
# )

# Refining the Spatial Scale for Maize Crop Agro-Climatological Suitability Conditions in a Region
# with Complex Topography towards a Smart and Sustainable Agriculture. Case Study: Central Romania (Cluj Count

# Maturity Hybrid,growing season length (days/y)
# Extremely early,76–85
# Early,86–112
# Intermediate,113–129
# Late,130–145
# Very late,>150

maize_variety_selector: Agent[UserContext] = Agent(
    name="Maize Variety Selector",
    handoff_description="An agent that can recommend suitable varieties of Maize",
    # 2.4 Request and log average seasonal rainfall (mm) and drought-risk pattern.
    instructions=(
        f"""{RECOMMENDED_PROMPT_PREFIX}
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
        """
    ),
    #
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
    tools=[elevation, soil_property, aez_classification, growing_period, maize_varieties],
    output_type=WhatsappResponse,
    model="gpt-4.1",
)

triage_agent: Agent[UserContext] = Agent(
    name="Triage Agent",
    handoff_description="A triage agent that can delegate a customer's request to the appropriate agent.",
    instructions=(
        f"""{RECOMMENDED_PROMPT_PREFIX} 
        You are a helpful triaging agent. You can use your tools to delegate questions to other appropriate agents.
        """
    ),
    handoffs=[
        # crop_suitability_agent,
        maize_variety_selector,
        # faq_agent,
        # handoff(agent=seat_booking_agent, on_handoff=on_seat_booking_handoff),
    ],
    output_type=WhatsappResponse,
    model="gpt-4.1-nano",
)

# crop_suitability_agent.handoffs.append(triage_agent)
maize_variety_selector.handoffs.append(triage_agent)

DEFAULT_AGENT = triage_agent.name

agents: dict[str, Agent] = {
    # crop_suitability_agent.name: crop_suitability_agent,
    triage_agent.name: triage_agent,
    maize_variety_selector.name: maize_variety_selector,
}


def get_all_agent_info() -> list[AgentInfo]:
    return [AgentInfo(key=agent_id, description=agent.handoff_description) for agent_id, agent in agents.items()]
