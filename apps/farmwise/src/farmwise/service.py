from datetime import UTC, datetime

from agents import Agent, Runner, RunResult, gen_trace_id, set_default_openai_key, trace
from farmbase_client import AuthenticatedClient
from farmbase_client.api.runresult import runresult_create_run_result as create_run_result
from farmbase_client.models import AgentBase, ChatState, RunResultCreate
from farmwise_schema.schema import ServiceMetadata, UserInput, WhatsAppResponse
from fastapi import APIRouter, FastAPI
from loguru import logger
from openai import OpenAI
from openai.types.responses import EasyInputMessageParam, ResponseInputImageParam, ResponseInputTextParam

from farmwise.agents import DEFAULT_AGENT, ONBOARDING_AGENT, agents, get_all_agent_info
from farmwise.dependencies import ChatStateDep, UserContext, UserContextDep
from farmwise.hooks import LoggingHooks
from farmwise.settings import settings

set_default_openai_key(settings.OPENAI_API_KEY.get_secret_value())
client = OpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())

app = FastAPI(debug=settings.is_dev())
router = APIRouter()


def create_openai_file(file_path):
    # This is more useful than sending base64, as it means the base64 does not get
    # sent back and forth repeatedly
    with open(file_path, "rb") as file_content:
        result = client.files.create(
            file=file_content,
            purpose="vision",
        )
        return result.id


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/info")
async def info() -> ServiceMetadata:
    return ServiceMetadata(agents=get_all_agent_info(), default_agent=DEFAULT_AGENT)


async def run_agent(
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
        file_id = create_openai_file(user_input.image)
        content.append(ResponseInputImageParam(detail="auto", file_id=file_id, type="input_image"))

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

    with AuthenticatedClient(base_url="http://127.0.0.1:8000/api/v1", token="fdsfds") as client:
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
    return result.final_output


@router.post("/invoke", response_model=WhatsAppResponse)
async def invoke(
    user_input: UserInput,
    context: UserContextDep,
    chat_state: ChatStateDep,
):
    if context.new_user:
        logger.info(f"NEW USER: {user_input.user_id}")
        agent = agents[ONBOARDING_AGENT]
    elif chat_state.last_agent:
        agent = agents[chat_state.last_agent.name]
    else:
        agent = agents[DEFAULT_AGENT]

    logger.info(f"USER: {user_input.message} AGENT: {agent.name} CONTEXT: {context}")
    return await run_agent(agent, context, user_input, chat_state)


app.include_router(router)
