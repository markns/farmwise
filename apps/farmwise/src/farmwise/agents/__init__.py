from collections import UserDict

from farmwise_schema.schema import AgentInfo
from loguru import logger

from .crop_pathogen_diagnosis_agent import crop_pathogen_diagnosis_agent
from .crop_suitability_agent import crop_suitability_agent
from .maize_variety_selector import maize_variety_selector
from .triage_agent import triage_agent

# Setup handoff relationships
triage_agent.handoffs = [
    crop_suitability_agent,
    maize_variety_selector,
    crop_pathogen_diagnosis_agent,
]

maize_variety_selector.handoffs = [
    crop_suitability_agent,
    triage_agent,
]

crop_suitability_agent.handoffs = [
    triage_agent,
    maize_variety_selector,
]

crop_pathogen_diagnosis_agent.handoffs = [
    triage_agent,
]

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
    },
)


def get_all_agent_info() -> list[AgentInfo]:
    return [AgentInfo(key=agent_id, description=agent.handoff_description) for agent_id, agent in agents.items()]
