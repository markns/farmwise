import logging
from datetime import datetime, timezone
from typing import Optional

from agents import ItemHelpers, Runner, RunResult, set_default_openai_key
from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from sqlalchemy import Column
from sqlmodel import JSON, Field, Session, SQLModel, create_engine, select

from farmwise.agents import AGENTS, triage_agent
from farmwise.context import AirlineAgentContext
from farmwise.settings import settings

logger = logging.getLogger(__name__)

set_default_openai_key(settings.OPENAI_API_KEY.get_secret_value())


app = FastAPI(debug=settings.is_dev())
router = APIRouter()


class UserInput(BaseModel):
    message: str
    uid: str


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    uid: str
    item: dict = Field(default_factory=dict, sa_column=Column(JSON))
    context: AirlineAgentContext | None = Field(sa_column=Column(JSON))
    agent: str | None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


engine = create_engine("sqlite:///farmwise.db")
SQLModel.metadata.create_all(engine)


@router.post("/invoke")
async def invoke(user_input: UserInput):
    with Session(engine) as session:
        statement = select(Message).where(Message.uid == user_input.uid).order_by(Message.id.desc()).limit(20)
        results = list(reversed(session.exec(statement).all()))
        previous_items = [row.item for row in results]

        agent = triage_agent
        if results and results[-1].agent in AGENTS:
            agent = AGENTS[results[-1].agent]
        if results:
            context = AirlineAgentContext.model_validate(results[-1].context)
        else:
            context = AirlineAgentContext()

    input_items = ItemHelpers.input_to_new_input_list(user_input.message)

    result: RunResult = await Runner.run(agent, previous_items + input_items, context=context)

    with Session(engine) as session:
        for item in input_items:
            session.add(Message(uid=user_input.uid, item=item))
        for item in result.new_items:
            session.add(
                Message(
                    uid=user_input.uid, item=item.to_input_item(), agent=item.agent.name, context=context.model_dump()
                )
            )
        session.commit()

    # return result.new_items
    return result.final_output


app.include_router(router)
