from typing import Annotated, List, Optional

from fastapi import Depends
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import true

from farmbase.auth.models import FarmbaseUser, FarmbaseUserOrganization
from farmbase.database.core import engine, DbSession
from farmbase.database.manage import init_schema
from farmbase.enums import UserRoles

from .models import Organization, OrganizationCreate, OrganizationRead, OrganizationUpdate


async def get(*, db_session: AsyncSession, organization_id: int) -> Optional[Organization]:
    """Gets an organization."""
    result = await db_session.execute(select(Organization).where(Organization.id == organization_id))
    return result.scalars().first()


async def get_default(*, db_session: AsyncSession) -> Optional[Organization]:
    """Gets the default organization."""
    result = await db_session.execute(select(Organization).where(Organization.default == true()))
    return result.scalars().one_or_none()


async def get_default_or_raise(*, db_session: AsyncSession) -> Organization:
    """Returns the default organization or raises ValidationError if one doesn't exist."""
    organization = await get_default(db_session=db_session)

    if not organization:
        raise ValidationError.from_exception_data(
            "OrganizationRead",
            [
                {
                    "loc": ("organization",),
                    "msg": "No default organization defined.",
                    "type": "value_error.not_found",
                }
            ],
        )
    return organization


async def get_by_name(*, db_session: AsyncSession, name: str) -> Optional[Organization]:
    """Gets an organization by its name."""
    result = await db_session.execute(select(Organization).where(Organization.name == name))
    return result.scalars().one_or_none()


async def get_by_name_or_raise(*, db_session: AsyncSession, organization_in: OrganizationRead) -> Organization:
    """Returns the organization specified or raises ValidationError."""
    organization = await get_by_name(db_session=db_session, name=organization_in.name)

    if not organization:
        raise ValidationError.from_exception_data(
            "OrganizationRead",
            [
                {
                    "loc": ("organization",),
                    "msg": f"Organization '{organization_in.name}' not found.",
                    "type": "value_error.not_found",
                }
            ],
        )

    return organization


async def get_by_slug(*, db_session: AsyncSession, slug: str) -> Optional[Organization]:
    """Gets an organization by its slug."""
    result = await db_session.execute(select(Organization).where(Organization.slug == slug))
    return result.scalars().one_or_none()


async def get_by_slug_or_raise(*, db_session: DbSession, organization: str) -> Organization:
    """Returns the organization specified or raises ValidationError."""
    organization = await get_by_slug(db_session=db_session, slug=organization)

    if not organization:
        raise ValidationError.from_exception_data(
            "OrganizationRead",
            [
                {
                    "loc": ("organization",),
                    "msg": f"Organization '{organization}' not found.",
                    "type": "value_error.not_found",
                }
            ],
        )

    return organization


CurrentOrganization = Annotated[Organization, Depends(get_by_slug_or_raise)]


async def get_by_name_or_default(*, db_session: AsyncSession, organization_in: OrganizationRead) -> Organization:
    """Returns an organization based on a name or the default if not specified."""
    if organization_in.name:
        return await get_by_name_or_raise(db_session=db_session, organization_in=organization_in)
    return await get_default_or_raise(db_session=db_session)


async def get_all(*, db_session: AsyncSession) -> List[Optional[Organization]]:
    """Gets all organizations."""
    result = await db_session.execute(select(Organization))
    return result.scalars().all()


async def create(*, db_session: AsyncSession, organization_in: OrganizationCreate) -> Organization:
    """Creates an organization."""
    organization = Organization(**organization_in.dict(exclude={"banner_color"}))
    if organization_in.banner_color:
        organization.banner_color = organization_in.banner_color.as_hex()
    # we let the new schema session create the organization
    organization = init_schema(engine=engine, organization=organization)
    return organization


async def get_or_create(*, db_session: AsyncSession, organization_in: OrganizationCreate) -> Organization:
    """Gets an existing or creates a new organization."""
    if organization_in.id:
        stmt = select(Organization).where(Organization.id == organization_in.id)
    else:
        filters = organization_in.dict(exclude={"id"})
        stmt = select(Organization).filter_by(**filters)
    result = await db_session.execute(stmt)
    instance = result.scalars().first()
    if instance:
        return instance
    return await create(db_session=db_session, organization_in=organization_in)


async def update(
    *, db_session: AsyncSession, organization: Organization, organization_in: OrganizationUpdate
) -> Organization:
    """Updates an organization."""
    organization_data = organization.dict()
    update_data = organization_in.model_dump(skip_defaults=True, exclude={"banner_color"})
    for field in organization_data:
        if field in update_data:
            setattr(organization, field, update_data[field])
    if organization_in.banner_color:
        organization.banner_color = organization_in.banner_color.as_hex()
    await db_session.commit()
    return organization


async def delete(*, db_session: AsyncSession, organization_id: int) -> None:
    """Deletes an organization."""
    result = await db_session.execute(select(Organization).where(Organization.id == organization_id))
    organization = result.scalars().first()
    if organization:
        await db_session.delete(organization)
        await db_session.commit()


async def add_user(
    *,
    db_session: AsyncSession,
    user: FarmbaseUser,
    organization: Organization,
    role: UserRoles = UserRoles.member,
) -> None:
    """Adds a user to an organization."""
    db_session.add(
        FarmbaseUserOrganization(
            farmbase_user_id=user.id,
            organization_id=organization.id,
            role=role,
        )
    )
    await db_session.commit()
