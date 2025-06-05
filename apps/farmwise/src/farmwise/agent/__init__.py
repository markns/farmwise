import functools
from collections import UserDict
from typing import Callable

from agents import HandoffInputData, RunContextWrapper, handoff
from loguru import logger
from pydantic import BaseModel, Field

from farmwise.schema import AgentInfo

from . import handoff_filters
from .crop_pathogen_diagnosis_agent import crop_pathogen_diagnosis_agent
from .crop_suitability_agent import crop_suitability_agent
from .maize_variety_selector import maize_variety_selector
from .onboarding_agent import onboarding_agent
from .soil_advisory_agent import soil_advisor
from .triage_agent import triage_agent


class HandoffInfo(BaseModel):
    agent_name: str = Field(description="The name of the agent being handed off to.")
    reason: str = Field(description="The reason for the handoff.")


async def on_handoff(ctx: RunContextWrapper[None], input_data: HandoffInfo):
    # nb. the agent_name and reason are non-deterministic,
    # they might not correspond to the actual handoff that happened
    logger.debug(f"Handoff to '{input_data.agent_name}' because '{input_data.reason}'")


def _apply_handoff_filters(
    functions: list[Callable[[HandoffInputData], HandoffInputData]], initial_data
) -> HandoffInputData:
    result = initial_data
    for func in functions:
        result = func(result)
    return result


triage_agent_handoff = handoff(
    agent=triage_agent,
    on_handoff=on_handoff,
    input_type=HandoffInfo,
    input_filter=functools.partial(
        _apply_handoff_filters,
        [
            handoff_filters.remove_whatsapp_interactivity,
            handoff_filters.remove_images,
        ],
    ),
)
crop_pathogen_diagnosis_agent_handoff = handoff(
    agent=crop_pathogen_diagnosis_agent,
    on_handoff=on_handoff,
    input_type=HandoffInfo,
    input_filter=handoff_filters.remove_whatsapp_interactivity,
)
crop_suitability_agent_handoff = handoff(
    agent=crop_suitability_agent,
    on_handoff=on_handoff,
    input_type=HandoffInfo,
    input_filter=handoff_filters.remove_whatsapp_interactivity,
)
maize_variety_selector_handoff = handoff(
    agent=maize_variety_selector,
    on_handoff=on_handoff,
    input_type=HandoffInfo,
    input_filter=handoff_filters.remove_whatsapp_interactivity,
)
soil_advisor_handoff = handoff(
    agent=soil_advisor,
    on_handoff=on_handoff,
    input_type=HandoffInfo,
    input_filter=handoff_filters.remove_whatsapp_interactivity,
)

handoffs = [
    triage_agent_handoff,
    crop_pathogen_diagnosis_agent_handoff,
    crop_suitability_agent_handoff,
    maize_variety_selector_handoff,
    soil_advisor_handoff,
]

triage_agent.handoffs = handoffs
maize_variety_selector.handoffs = [triage_agent_handoff]
crop_suitability_agent.handoffs = [triage_agent_handoff]
crop_pathogen_diagnosis_agent.handoffs = [triage_agent_handoff]
onboarding_agent.handoffs = [triage_agent_handoff]
soil_advisor.handoffs = [triage_agent_handoff]

ONBOARDING_AGENT = onboarding_agent.name
DEFAULT_AGENT = triage_agent.name


class AgentDict(UserDict):
    def __init__(self, default_agent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_agent = default_agent

    def __getitem__(self, key):
        if key is None:
            logger.debug("Using default agent")
            return self.default_agent
        elif key in self.data:
            return self.data[key]
        else:
            raise KeyError(f"Agent '{key}' not found.")


agents = AgentDict(
    triage_agent,
    {
        triage_agent.name: triage_agent,
        maize_variety_selector.name: maize_variety_selector,
        crop_suitability_agent.name: crop_suitability_agent,
        crop_pathogen_diagnosis_agent.name: crop_pathogen_diagnosis_agent,
        onboarding_agent.name: onboarding_agent,
        soil_advisor.name: soil_advisor,
    },
)


def get_all_agent_info() -> list[AgentInfo]:
    return [AgentInfo(key=agent_id, description=agent.handoff_description) for agent_id, agent in agents.items()]
