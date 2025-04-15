from __future__ import annotations as _annotations

from agents import (
    Agent,
    handoff,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from farmwise_schema.schema import AgentInfo

from farmwise.context import UserContext
from farmwise.hooks import on_seat_booking_handoff
from farmwise.tools import faq_lookup_tool, update_seat

# TODO: Split into separate modules, as shown in openai-agents-python/examples/financial_research_agent

faq_agent = Agent[UserContext](
    name="FAQ Agent",
    handoff_description="A helpful agent that can answer questions about the airline.",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are an FAQ agent. If you are speaking to a customer, you probably were transferred to from the triage agent.
    Use the following routine to support the customer.
    # Routine
    1. Identify the last question asked by the customer.
    2. Use the faq lookup tool to answer the question. Do not rely on your own knowledge.
    3. If you cannot answer the question, transfer back to the triage agent.""",
    tools=[faq_lookup_tool],
)

seat_booking_agent = Agent[UserContext](
    name="Seat Booking Agent",
    handoff_description="A helpful agent that can update a seat on a flight.",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a seat booking agent. If you are speaking to a customer, you probably were transferred to from the triage agent.
    Use the following routine to support the customer.
    # Routine
    1. Ask for their confirmation number.
    2. Ask the customer what their desired seat number is.
    3. Use the update seat tool to update the seat on the flight.
    If the customer asks a question that is not related to the routine, transfer back to the triage agent. """,
    tools=[update_seat],
)

onboarding_agent = Agent[UserContext](
    name="Onboarding Agent",
    handoff_description="A helpful agent that onboards farmers into the FarmWise system.",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are an onboarding agent. If you are speaking to a customer, you probably were transferred to from the triage agent.
    Use the following routine to support the customer.
    # Routine
    1. Ask for their confirmation number.
    2. Ask the customer what their desired seat number is.
    3. Use the update seat tool to update the seat on the flight.
    If the customer asks a question that is not related to the routine, transfer back to the triage agent. """,
    tools=[update_seat],
)

triage_agent = Agent[UserContext](
    name="Triage Agent",
    handoff_description="A triage agent that can delegate a customer's request to the appropriate agent.",
    instructions=(
        f"{RECOMMENDED_PROMPT_PREFIX} "
        "You are a helpful triaging agent. You can use your tools to delegate questions to other appropriate agents."
    ),
    handoffs=[
        faq_agent,
        handoff(agent=seat_booking_agent, on_handoff=on_seat_booking_handoff),
    ],
    model="gpt-3.5-turbo",
)

faq_agent.handoffs.append(triage_agent)
seat_booking_agent.handoffs.append(triage_agent)

DEFAULT_AGENT = triage_agent.name

agents: dict[str, Agent] = {
    faq_agent.name: faq_agent,
    seat_booking_agent.name: seat_booking_agent,
    triage_agent.name: triage_agent,
}

# agents: dict[str, Agent] = {
#     "chatbot": Agent(description="A simple chatbot.", graph=chatbot),
#     "research-assistant": Agent(
#         description="A research assistant with web search and calculator.", graph=research_assistant
#     ),
#     "command-agent": Agent(description="A command agent.", graph=command_agent),
#     "bg-task-agent": Agent(description="A background task agent.", graph=bg_task_agent),
#     "langgraph-supervisor-agent": Agent(
#         description="A langgraph supervisor agent", graph=langgraph_supervisor_agent
#     ),
#     "interrupt-agent": Agent(description="An agent the uses interrupts.", graph=interrupt_agent),
# }


def get_all_agent_info() -> list[AgentInfo]:
    return [AgentInfo(key=agent_id, description=agent.handoff_description) for agent_id, agent in agents.items()]
