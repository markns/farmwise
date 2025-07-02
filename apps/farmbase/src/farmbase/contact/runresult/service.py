from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from farmbase.contact import service as contact_service

from .models import Agent, RunResult, RunResultCreate


async def get_or_create_agent_by_name(*, db_session: AsyncSession, name: str) -> Agent:
    """Find an Agent by name or create a new one."""
    stmt = select(Agent).where(Agent.name == name)
    result = await db_session.execute(stmt)
    agent = result.scalar_one_or_none()

    if agent:
        return agent

    agent = Agent(name=name)
    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)
    return agent


async def create(*, db_session: AsyncSession, run_result_in: RunResultCreate) -> RunResult:
    """Creates a Run Result."""

    contact = await contact_service.get(db_session=db_session, contact_id=run_result_in.contact_id)
    agent = await get_or_create_agent_by_name(db_session=db_session, name=run_result_in.last_agent.name)
    run_result = RunResult(
        contact=contact,
        last_agent=agent,
        **run_result_in.model_dump(exclude={"contact", "last_agent"}),
    )

    db_session.add(run_result)
    await db_session.commit()
    return run_result


async def get_latest(*, db_session: AsyncSession, contact_id: int) -> RunResult:
    """Returns a Run Result based on the given run result id."""
    result = await db_session.execute(
        select(RunResult)
        .options(selectinload(RunResult.last_agent))
        .where(RunResult.contact_id == contact_id)
        .order_by(RunResult.id.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()
