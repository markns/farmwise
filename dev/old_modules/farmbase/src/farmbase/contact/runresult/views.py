from fastapi import APIRouter

from farmbase.database.core import DbSession

from .models import RunResultCreate
from .service import create

router = APIRouter()


@router.post(
    "",
    response_model=str,
    summary="Create a new run_result for a contact.",
    # dependencies=[Depends(PermissionsDependency([ContactCreatePermission]))],
)
async def create_run_result(
    contact_id: int,
    db_session: DbSession,
    run_result_in: RunResultCreate,
):
    """Create a new run_result."""
    run_result = await create(db_session=db_session, run_result_in=run_result_in)
    # TODO: What to return here?
    return "OK"
