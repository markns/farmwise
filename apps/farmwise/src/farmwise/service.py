import logging
from datetime import datetime, timezone
from typing import Annotated, Any, Optional

from agents import Agent, ItemHelpers, MessageOutputItem, Runner, RunResult, gen_trace_id, set_default_openai_key, trace
from farmwise_schema.schema import ChatHistory, ChatHistoryInput, ChatMessage, ServiceMetadata, UserInput
from fastapi import APIRouter, Depends, FastAPI
from openai.types.responses import EasyInputMessageParam
from sqlmodel import Field, Session, SQLModel, create_engine, select

from farmwise.agents import DEFAULT_AGENT, agents, get_all_agent_info
from farmwise.context import UserContext, UserContextDep
from farmwise.settings import settings

logger = logging.getLogger(__name__)

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


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    role: str
    content: str
    agent: str | None
    # user_name: str | None  # Todo: normalize to users table
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    trace_id: str | None


engine = create_engine("sqlite:///farmwise.db")
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def chat_history(user_input: UserInput, session: Session = Depends(get_session)):
    statement = (
        select(Message.role, Message.content).where(Message.user_id == user_input.user_id).order_by(Message.id.desc())
    )
    results = [
        EasyInputMessageParam(role=row.role, content=row.content) for row in reversed(session.exec(statement).all())
    ]
    return results


def current_agent(user_input: UserInput, session: Session = Depends(get_session)):
    statement = select(Message.agent).where(Message.user_id == user_input.user_id).order_by(Message.id.desc()).limit(1)

    try:
        return agents[session.exec(statement).one_or_none()]
    except KeyError:
        return agents[DEFAULT_AGENT]


@router.post("/invoke", response_model=ChatMessage)
async def invoke(
    user_input: UserInput,
    context: UserContextDep,
    history: Annotated[Any, Depends(chat_history)],
    agent: Annotated[Agent[UserContext], Depends(current_agent)],
):
    input_item = EasyInputMessageParam(content=user_input.message, role="user")

    trace_id = gen_trace_id()
    with trace("FarmWise", trace_id=trace_id, group_id=user_input.user_id):
        result: RunResult = await Runner.run(agent, history + [input_item], context=context)

    with Session(engine) as session:
        session.add(
            Message(
                user_id=user_input.user_id,
                content=input_item["content"],
                role=input_item["role"],
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
                    )
                )
        session.commit()

    return ChatMessage(type="assistant", content=result.final_output)


@router.post("/history")
def history(input: ChatHistoryInput) -> ChatHistory:
    """
    Get chat history.
    """
    try:
        with Session(engine) as session:
            statement = (
                select(Message)
                .where(Message.user_id == input.user_id, Message.thread_id == input.thread_id)
                .order_by(Message.id.desc())
            )
            results = list(reversed(session.exec(statement).all()))
            previous_items = [row.item for row in results]

        return ChatHistory(messages=chat_messages)
    except Exception as e:
        logger.error(f"An exception occurred: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error")


app.include_router(router)
