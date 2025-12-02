from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.apps.app import EventsCompactionConfig
from google.adk.plugins.global_instruction_plugin import GlobalInstructionPlugin

from farmwise.tools.courses import available_courses

from .prompt import triage_agent_instructions
from .shared_libraries.callbacks import before_agent
from .sub_agents.crop_pathogen_diagnosis_agent.agent import crop_pathogen_diagnosis_agent
from .sub_agents.crop_suitability_agent.agent import crop_suitability_agent
from .sub_agents.onboarding_agent.agent import onboarding_agent
from .sub_agents.soil_advisory_agent.agent import soil_advisor_agent

root_agent = Agent(
    model="gemini-2.5-flash",
    name="TriageAgent",
    description="""Provides personalized agronomic advice and manages farm records. Ideal for queries on
    crop planning, pest management, input optimization, and farm data updates. Transfer back to this agent when the
    message from the user isn't relevant to your instructions.""",
    instruction=triage_agent_instructions,
    tools=[available_courses],
    sub_agents=[
        crop_pathogen_diagnosis_agent,
        crop_suitability_agent,
        onboarding_agent,
        soil_advisor_agent,
    ],
    before_agent_callback=before_agent,
)

# https://google.github.io/adk-docs/apps/
# https://github.com/google/adk-python/commit/4df79dd5c92d96096d031b26470458d0bca79a79#diff-16ec21c8fc1d0d3df69ff9115b1c1f8f52aa850265492a5fccb02b4b50459cc3
app = App(
    name="assistant",
    root_agent=root_agent,
    plugins=[
        # CountInvocationPlugin(),
        # ContextFilterPlugin(num_invocations_to_keep=3),
        # SaveFilesAsArtifactsPlugin(),
        GlobalInstructionPlugin(
            global_instruction="""You are a helpful assistant for farmbetter. 
            We empower farmers and organisations with digital extension for regenerative agriculture to 
            build climate resilience in sub-Saharan Africa, Asia & Latin America.
            
            Your mission is to support farmers, cooperatives, and agribusiness stakeholders in East Africa
            by providing personalized agronomic advice and maintaining accurate farm records. 
            """
        )
    ],
    # Enable event compaction with an LLM-based summarizer.
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=2,
        overlap_size=1,
    ),
)
