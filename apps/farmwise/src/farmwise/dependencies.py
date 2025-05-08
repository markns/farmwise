from farmwise_schema.schema import UserInput
from fastapi import Depends
from openai.types.responses import EasyInputMessageParam
from sqlmodel import Session, select

from farmwise.agents import DEFAULT_AGENT, agents
from farmwise.context import UserContext
from farmwise.database import Message, get_session


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


async def user_context(user_input: UserInput, session: Session = Depends(get_session)):
    # user = await users_service.get_by_id(token_data["user_id"])
    # if not user["is_active"]:
    #     raise UserIsBanned()
    #
    # if not user["is_creator"]:
    #     raise UserNotCreator()

    #   todo: get or create user

    return UserContext(user_id=1, phone_number=user_input.user_id, organization="default")
