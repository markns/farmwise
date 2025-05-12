from typing import Annotated

from agents import ItemHelpers, MessageOutputItem, Runner, RunResult, gen_trace_id, set_default_openai_key, trace
from farmwise_schema.schema import ServiceMetadata, UserInput, WhatsappResponse
from fastapi import APIRouter, Depends, FastAPI
from loguru import logger
from openai.types.responses import EasyInputMessageParam, ResponseInputImageParam
from sqlmodel import Session

from farmwise.agents import DEFAULT_AGENT, agents, get_all_agent_info
from farmwise.context import UserContext
from farmwise.database import Message, engine
from farmwise.dependencies import ChatStateDep, user_context
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
    context: Annotated[UserContext, Depends(user_context)],
    chat_state: ChatStateDep,
):
    agent = agents[chat_state.current_agent]

    logger.info(f"USER: {user_input.message} CONTEXT: {context} STATE: {chat_state}")
    input_items = [EasyInputMessageParam(content=user_input.message, role="user")]
    if user_input.image:
        input_items.append(
            EasyInputMessageParam(
                content=[
                    ResponseInputImageParam(
                        detail="auto", image_url=f"data:image/jpeg;base64,{user_input.image}", type="input_image"
                    )
                ],
                role="user",
            ),
        )

    trace_id = gen_trace_id()
    with trace("FarmWise", trace_id=trace_id, group_id=user_input.user_id):
        result: RunResult = await Runner.run(
            agent,
            input=input_items,
            context=context,
            previous_response_id=chat_state.previous_response_id,
        )

    with Session(engine) as session:
        session.add(
            Message(
                user_id=user_input.user_id,
                content=input_items[0]["content"],
                role=input_items[0]["role"],
                timestamp=user_input.timestamp,
                trace_id=trace_id,
            )
        )
        for item in result.new_items:
            # todo: do we also want to persist other items here too? (eg. ReasoningItems)
            if isinstance(item, MessageOutputItem):
                session.add(
                    Message(
                        user_id=user_input.user_id,
                        content=ItemHelpers.text_message_output(item),
                        role=item.raw_item.role,
                        agent=item.agent.name,
                        trace_id=trace_id,
                        previous_response_id=result.last_response_id,
                    )
                )
        session.commit()

    logger.info(f"ASSISTANT: {result.final_output}")
    return result.final_output


# @router.post("/history")
# def history(input: ChatHistoryInput) -> ChatHistory:
#     """
#     Get chat history.
#     """
#     try:
#         with Session(engine) as session:
#             statement = (
#                 select(Message)
#                 .where(Message.user_id == input.user_id, Message.thread_id == input.thread_id)
#                 .order_by(Message.id.desc())
#             )
#             results = list(reversed(session.exec(statement).all()))
#             previous_items = [row.item for row in results]
#
#         return ChatHistory(messages=chat_messages)
#     except Exception as e:
#         logger.error(f"An exception occurred: {e}")
#         raise HTTPException(status_code=500, detail="Unexpected error")


app.include_router(router)
