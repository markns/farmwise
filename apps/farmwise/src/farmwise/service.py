from datetime import UTC, datetime

from agents import Runner, RunResult, gen_trace_id, set_default_openai_key, trace
from farmbase_client import AuthenticatedClient
from farmbase_client.api.runresult import runresult_create_run_result as create_run_result
from farmbase_client.models import AgentBase, RunResultCreate
from farmwise_schema.schema import ServiceMetadata, UserInput, WhatsappResponse
from fastapi import APIRouter, FastAPI
from loguru import logger
from openai.types.responses import EasyInputMessageParam, ResponseInputImageParam, ResponseInputTextParam

from farmwise.agents import DEFAULT_AGENT, agents, get_all_agent_info
from farmwise.dependencies import ChatStateDep, UserContextDep
from farmwise.settings import settings

set_default_openai_key(settings.OPENAI_API_KEY.get_secret_value())

app = FastAPI(debug=settings.is_dev())
router = APIRouter()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/info")
async def info() -> ServiceMetadata:
    return ServiceMetadata(agents=get_all_agent_info(), default_agent=DEFAULT_AGENT)


@router.post("/invoke", response_model=WhatsappResponse)
async def invoke(
    user_input: UserInput,
    context: UserContextDep,
    chat_state: ChatStateDep,
):
    if context.new_user:
        logger.info(f"NEW USER: {user_input.user_id}")

    if chat_state.last_agent:
        agent = agents[chat_state.last_agent.name]
    else:
        agent = agents[DEFAULT_AGENT]

    logger.info(f"USER: {user_input.message} CONTEXT: {context} LAST_AGENT: {chat_state.last_agent}")

    input_items = chat_state.input_list

    if user_input.image:
        input_items.append(
            EasyInputMessageParam(
                content=[
                    ResponseInputTextParam(text=user_input.message, type="input_text"),
                    ResponseInputImageParam(
                        detail="auto", image_url=f"data:image/jpeg;base64,{user_input.image}", type="input_image"
                    ),
                ],
                role="user",
            ),
        )
    else:
        input_items.append(
            EasyInputMessageParam(content=user_input.message, role="user"),
        )

    trace_id = gen_trace_id()
    with trace("FarmWise", trace_id=trace_id, group_id=user_input.user_id):
        result: RunResult = await Runner.run(
            agent,
            input=input_items,
            context=context,
        )

    with AuthenticatedClient(base_url="http://127.0.0.1:8000/api/v1", token="fdsfds") as client:
        await create_run_result.asyncio(
            client=client,
            organization=context.organization,
            body=RunResultCreate(
                contact_id=context.user_id,
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


app.include_router(router)
