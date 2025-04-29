from typing import List, Optional

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import true

from .models import Project, ProjectCreate, ProjectRead, ProjectUpdate


async def get(*, db_session: AsyncSession, project_id: int) -> Project | None:
    """Returns a project based on the given project id."""
    result = await db_session.execute(select(Project).where(Project.id == project_id))
    return result.scalars().first()


async def get_default(*, db_session: AsyncSession) -> Optional[Project]:
    """Returns the default project."""
    result = await db_session.execute(select(Project).where(Project.default == true()))
    return result.scalars().one_or_none()


async def get_default_or_raise(*, db_session: AsyncSession) -> Project:
    """Returns the default project or raises a ValidationError if one doesn't exist."""
    project = await get_default(db_session=db_session)

    if not project:
        raise ValidationError.from_exception_data(
            "ProjectRead",
            [
                {
                    "loc": ("project",),
                    "msg": "No default project defined.",
                    "type": "value_error.not_found",
                }
            ],
        )
    return project


async def get_by_name(*, db_session: AsyncSession, name: str) -> Optional[Project]:
    """Returns a project based on the given project name."""
    result = await db_session.execute(select(Project).where(Project.name == name))
    return result.scalars().one_or_none()


async def get_by_name_or_raise(*, db_session: AsyncSession, project_in: ProjectRead) -> Project:
    """Returns the project specified or raises ValidationError."""
    project = await get_by_name(db_session=db_session, name=project_in.name)

    if not project:
        raise ValidationError.from_exception_data(
            "ProjectRead",
            [
                {
                    "loc": ("name",),
                    "msg": f"Project '{project_in.name}' not found.",
                    "type": "value_error.not_found",
                }
            ],
        )

    return project


async def get_by_name_or_default(*, db_session: AsyncSession, project_in: ProjectRead) -> Project:
    """Returns a project based on a name or the default if not specified."""
    if project_in:
        if project_in.name:
            return await get_by_name_or_raise(db_session=db_session, project_in=project_in)
    return await get_default_or_raise(db_session=db_session)


async def get_all(*, db_session: AsyncSession) -> List[Optional[Project]]:
    """Returns all projects."""
    result = await db_session.execute(select(Project))
    return result.scalars().all()


async def create(*, db_session: AsyncSession, project_in: ProjectCreate) -> Project:
    """Creates a project."""
    from farmbase.organization import service as organization_service

    organization = await organization_service.get_by_slug(db_session=db_session, slug=project_in.organization.slug)
    project = Project(
        **project_in.model_dump(exclude={"organization"}),
        organization_id=organization.id,
    )

    db_session.add(project)
    await db_session.commit()
    return project


async def get_or_create(*, db_session: AsyncSession, project_in: ProjectCreate) -> Project:
    if project_in.id:
        stmt = select(Project).where(Project.id == project_in.id)
    else:
        filters = project_in.model_dump(exclude={"id", "organization"})
        stmt = select(Project).filter_by(**filters)

    result = await db_session.execute(stmt)
    instance = result.scalars().first()
    if instance:
        return instance

    return await create(db_session=db_session, project_in=project_in)


async def update(*, db_session: AsyncSession, project: Project, project_in: ProjectUpdate) -> Project:
    """Updates a project."""
    project_data = project.dict()

    update_data = project_in.model_dump(skip_defaults=True, exclude={})

    for field in project_data:
        if field in update_data:
            setattr(project, field, update_data[field])

    await db_session.commit()
    return project


async def delete(*, db_session: AsyncSession, project_id: int) -> None:
    """Deletes a project."""
    result = await db_session.execute(select(Project).where(Project.id == project_id))
    project = result.scalars().first()
    if project:
        await db_session.delete(project)
        await db_session.commit()
