import io
from datetime import UTC, datetime

import requests
from agents import Agent, Runner, RunResult, gen_trace_id, trace
from agents.voice import SingleAgentVoiceWorkflow, TTSModelSettings, VoicePipeline, VoicePipelineConfig
from farmbase_client import AuthenticatedClient
from farmbase_client.api.runresult import runresult_create_run_result as create_run_result
from farmbase_client.models import AgentBase, ChatState, RunResultCreate
from loguru import logger
from openai import OpenAI
from openai.types.responses import EasyInputMessageParam, ResponseInputImageParam, ResponseInputTextParam

from farmwise.agent import DEFAULT_AGENT, ONBOARDING_AGENT, agents
from farmwise.audio import load_oga_as_audio_input, write_stream_to_ogg
from farmwise.dependencies import UserContext, chat_state, user_context
from farmwise.hooks import LoggingHooks
from farmwise.schema import UserInput, WhatsAppResponse
from farmwise.settings import settings


class FarmwiseService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())

    def create_openai_file(self, file_url):
        # This is more useful than sending base64, as it means the base64 does not get
        # sent back and forth repeatedly

        response = requests.get(file_url)
        response.raise_for_status()

        # Determine a filename from the URL (or default to something)
        filename = file_url.split("/")[-1] or "upload.jpg"

        # Make sure the filename has a supported extension
        if not any(filename.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]):
            raise ValueError(f"Unsupported file extension in: {filename}")

        file_like = io.BytesIO(response.content)
        file_like.name = filename  # This is critical — OpenAI expects a `.name` attribute

        logger.debug(f"Sending file {filename} from {file_url} to OpenAI")
        logger.debug(f"Sending file from {file_url} to OpenAI")
        result = self.openai_client.files.create(
            file=file_like,
            purpose="vision",
        )
        logger.debug(f"Created file {result}")
        return result.id

    # async def get_info(self) -> ServiceMetadata:
    #     return ServiceMetadata(agents=get_all_agent_info(), default_agent=DEFAULT_AGENT)

    async def run_agent(
        self,
        agent: Agent[UserContext],
        context: UserContext,
        user_input: UserInput,
        chat_state: ChatState,
    ):
        input_items = chat_state.input_list

        content = []
        if user_input.message:
            content.append(ResponseInputTextParam(text=user_input.message, type="input_text"))
        if user_input.image:
            file_id = self.create_openai_file(user_input.image)
            content.extend(
                [
                    ResponseInputImageParam(detail="auto", file_id=file_id, type="input_image"),
                    ResponseInputTextParam(text=f"image_path={user_input.image}", type="input_text"),
                ]
            )

        input_items.append(
            EasyInputMessageParam(
                content=content,
                role="user",
            )
        )

        trace_id = gen_trace_id()
        hooks = LoggingHooks()
        with trace("FarmWise", trace_id=trace_id, group_id=user_input.user_id):
            result: RunResult = await Runner.run(agent, input=input_items, context=context, hooks=hooks)

        with AuthenticatedClient(base_url=settings.FARMBASE_ENDPOINT, token=settings.FARMBASE_API_KEY) as client:
            await create_run_result.asyncio(
                client=client,
                organization=context.contact.organization.slug,
                body=RunResultCreate(
                    contact_id=context.contact.id,
                    created_at=datetime.now(UTC),
                    input=result.input,
                    final_output=result.final_output,
                    input_guardrails=None,
                    output_guardrails=None,
                    last_agent=AgentBase(name=result.last_agent.name),
                    new_items=[],  # TODO: do we want to persist new_items and raw_responses?
                    raw_responses=[],
                    input_list=result.to_input_list(),
                    trace_id=trace_id,
                    # todo:
                    #  add tokens
                ),
            )

        logger.info(f"ASSISTANT: {result.final_output}")
        # return result.final_output

    async def invoke(self, user_input: UserInput) -> WhatsAppResponse:
        context = await user_context(user_input)
        chat_state_obj = await chat_state(context)

        if context.new_user:
            logger.info(f"NEW USER: {user_input.user_id}")
            agent = agents[ONBOARDING_AGENT]
        elif chat_state_obj.last_agent:
            agent = agents[chat_state_obj.last_agent.name]
        else:
            agent = agents[DEFAULT_AGENT]

        logger.info(f"USER: {user_input.message} AGENT: {agent.name} CONTEXT: {context}")
        return await self.run_agent(agent, context, user_input, chat_state)

    async def invoke_voice(self, user_input: UserInput) -> str:
        agent = agents[DEFAULT_AGENT]

        audio_input = load_oga_as_audio_input(user_input.voice)

        print(f"loaded audio input {audio_input}")
        pipeline = VoicePipeline(
            workflow=SingleAgentVoiceWorkflow(agent),
            config=VoicePipelineConfig(workflow_name="FarmWise", tts_settings=TTSModelSettings(voice="onyx")),
        )

        result = await pipeline.run(audio_input)

        output_path = user_input.voice.replace(".oga", "_response.oga")
        await write_stream_to_ogg(result.stream(), output_path)

        return output_path


farmwise = FarmwiseService()
