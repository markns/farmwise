# @background_task
from farmbase.organization.models import Organization


async def contact_init_flow(*, contact_id: int, organization: Organization, db_session=None):
    """Initializes a new contact with default settings."""
    # contact = await get(db_session=db_session, contact_id=contact_id)
    ...
