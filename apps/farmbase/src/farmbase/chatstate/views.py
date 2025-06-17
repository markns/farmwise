from typing import Sequence

from fastapi import APIRouter

from farmbase.database.core import DbSession
from farmbase.message import service as message_service
from farmbase.message.models import Message
from farmbase.runresult import service as run_result_service
from farmbase.runresult.models import AgentRead

from .models import ChatState

router = APIRouter()


def _to_input_list(messages: Sequence[Message]):
    return [
        {
            "role": "assistant",
            "content": [{"text": message.text, "type": "input_text"}],
        }
        for message in messages
    ]


@router.get(
    "",
    response_model=ChatState,
    summary="Get the latest chat state",
)
async def get_chat_state(db_session: DbSession, contact_id: int):
    run_result = await run_result_service.get_latest(db_session=db_session, contact_id=contact_id)
    if not run_result:
        messages = await message_service.get(db_session=db_session, contact_id=contact_id)
        return ChatState(last_agent=None, messages=_to_input_list(messages))

    messages = await message_service.get(db_session=db_session, contact_id=contact_id, since=run_result.created_at)
    input_list = run_result.input_list + _to_input_list(messages)

    return ChatState(
        last_agent=AgentRead(
            id=run_result.last_agent.id,
            name=str(run_result.last_agent.name),
        ),
        messages=input_list,
    )
