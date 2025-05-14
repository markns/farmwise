from fastapi import APIRouter
from loguru import logger

from farmbase.database.core import DbSession
from farmbase.messages.models import AgentRead, ChatState, RunResultCreate
from farmbase.messages.service import create, get

router = APIRouter()


@router.post(
    "/run_result",
    response_model=str,
    summary="Create a new run_result.",
    # dependencies=[Depends(PermissionsDependency([ContactCreatePermission]))],
)
async def create_run_result(
    db_session: DbSession,
    run_result_in: RunResultCreate,
):
    """Create a new run_result."""
    logger.warning(run_result_in)
    run_result = await create(db_session=db_session, run_result_in=run_result_in)
    return "OK"


@router.get(
    "",
    response_model=ChatState,
    summary="Get the latest chat state",
)
async def get_chat_state(db_session: DbSession, contact_id: int):
    run_result = await get(db_session=db_session, contact_id=contact_id)
    if not run_result:
        return ChatState()

    return ChatState(
        last_agent=AgentRead(
            id=run_result.last_agent.id,
            name=run_result.last_agent.name,
        ),
        input_list=run_result.input_list,
    )
