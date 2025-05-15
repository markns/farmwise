from fastapi import APIRouter
from loguru import logger

from farmbase.database.core import DbSession

from .models import RunResultCreate
from .service import create

router = APIRouter()


@router.post(
    "",
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
