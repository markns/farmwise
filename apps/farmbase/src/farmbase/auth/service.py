import logging
from typing import Annotated, Optional

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from farmbase.config import (
    FARMBASE_AUTHENTICATION_DEFAULT_USER,
    FARMBASE_AUTHENTICATION_PROVIDER_SLUG,
)
from farmbase.enums import UserRoles
from farmbase.organization import service as organization_service
from farmbase.organization.models import OrganizationRead
from farmbase.plugins.base import plugins
from farmbase.project import service as project_service
from farmbase.project.models import ProjectBase

from .models import (
    FarmbaseUser,
    FarmbaseUserOrganization,
    FarmbaseUserProject,
    UserCreate,
    UserOrganization,
    UserProject,
    UserRegister,
    UserUpdate,
)

log = logging.getLogger(__name__)

InvalidCredentialException = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED, detail=[{"msg": "Could not validate credentials"}]
)


async def get(*, db_session: AsyncSession, user_id: int) -> Optional[FarmbaseUser]:
    """Returns a user based on the given user id."""
    result = await db_session.execute(
        select(FarmbaseUser).where(FarmbaseUser.id == user_id)
        # .options(selectinload(FarmbaseUser.organizations).selectinload(FarmbaseUserOrganization.organization))
    )
    return result.scalars().one_or_none()


async def get_by_email(*, db_session: AsyncSession, email: str) -> Optional[FarmbaseUser]:
    """Returns a user object based on user email."""
    result = await db_session.execute(
        select(FarmbaseUser)
        .where(FarmbaseUser.email == email)
        .options(selectinload(FarmbaseUser.organizations).selectinload(FarmbaseUserOrganization.organization))
    )
    return result.scalars().one_or_none()


async def create_or_update_project_role(*, db_session: AsyncSession, user: FarmbaseUser, role_in: UserProject):
    """Creates a new project role or updates an existing role."""
    # determine project id
    if not role_in.project.id:
        project = await project_service.get_by_name(db_session=db_session, name=role_in.project.name)
        project_id = project.id
    else:
        project_id = role_in.project.id

    # fetch existing role
    result = await db_session.execute(
        select(FarmbaseUserProject).where(
            FarmbaseUserProject.farmbase_user_id == user.id,
            FarmbaseUserProject.project_id == project_id,
        )
    )
    project_role = result.scalars().one_or_none()

    # create or update
    if not project_role:
        return FarmbaseUserProject(project_id=project_id, role=role_in.role)
    project_role.role = role_in.role
    return project_role


async def create_or_update_project_default(
    *, db_session: AsyncSession, user: FarmbaseUser, user_project_in: UserProject
):
    """Creates a new user project or updates an existing one."""
    # determine project id
    if user_project_in.project.id:
        project_id = user_project_in.project.id
    else:
        project = await project_service.get_by_name(db_session=db_session, name=user_project_in.project.name)
        project_id = project.id

    # fetch existing user project
    result = await db_session.execute(
        select(FarmbaseUserProject).where(
            FarmbaseUserProject.farmbase_user_id == user.id,
            FarmbaseUserProject.project_id == project_id,
        )
    )
    user_project = result.scalars().one_or_none()

    # create new default or update existing
    if not user_project:
        user_project = FarmbaseUserProject(
            farmbase_user_id=user.id,
            project_id=project_id,
            default=True,
        )
        db_session.add(user_project)
        return user_project
    user_project.default = user_project_in.default
    return user_project


async def create_or_update_organization_role(
    *, db_session: AsyncSession, user: FarmbaseUser, role_in: UserOrganization
):
    """Creates a new organization role or updates an existing role."""
    # determine organization id
    if not role_in.organization.id:
        organization = await organization_service.get_by_name(db_session=db_session, name=role_in.organization.name)
        organization_id = organization.id
    else:
        organization_id = role_in.organization.id

    # fetch existing organization role
    result = await db_session.execute(
        select(FarmbaseUserOrganization).where(
            FarmbaseUserOrganization.farmbase_user_id == user.id,
            FarmbaseUserOrganization.organization_id == organization_id,
        )
    )
    organization_role = result.scalars().one_or_none()

    # create or update role
    if not organization_role:
        return FarmbaseUserOrganization(organization_id=organization_id, role=role_in.role)
    organization_role.role = role_in.role
    return organization_role


async def create(*, db_session: AsyncSession, organization: str, user_in: (UserRegister | UserCreate)) -> FarmbaseUser:
    """Creates a new farmbase user."""
    # pydantic forces a string password, but we really want bytes
    password = bytes(user_in.password, "utf-8")

    # create the user
    user = FarmbaseUser(
        **user_in.model_dump(exclude={"password", "organizations", "projects", "role"}), password=password
    )

    org = await organization_service.get_by_slug_or_raise(
        db_session=db_session,
        organization_in=OrganizationRead(name=organization, slug=organization),
    )

    # add user to the current organization
    role = UserRoles.member
    if hasattr(user_in, "role"):
        role = user_in.role

    user.organizations.append(FarmbaseUserOrganization(organization=org, role=role))

    projects = []
    if user_in.projects:
        # we reset the default value for all user projects
        for user_project in user.projects:
            user_project.default = False

        for user_project in user_in.projects:
            projects.append(
                await create_or_update_project_default(db_session=db_session, user=user, user_project_in=user_project)
            )
    else:
        # get the default project
        default_project = await project_service.get_default_or_raise(db_session=db_session)
        projects.append(
            await create_or_update_project_default(
                db_session=db_session,
                user=user,
                user_project_in=UserProject(project=ProjectBase(**default_project.dict())),
            )
        )
    user.projects = projects

    db_session.add(user)
    await db_session.commit()
    return user


async def get_or_create(*, db_session: AsyncSession, organization: str, user_in: UserRegister) -> FarmbaseUser:
    """Gets an existing user or creates a new one."""
    user = await get_by_email(db_session=db_session, email=user_in.email)

    if not user:
        try:
            user = await create(db_session=db_session, organization=organization, user_in=user_in)
        except IntegrityError:
            await db_session.rollback()
            log.exception(f"Unable to create user with email address {user_in.email}.")

    return user


async def update(*, db_session: AsyncSession, user: FarmbaseUser, user_in: UserUpdate) -> FarmbaseUser:
    """Updates a user."""
    user_data = user.dict()

    update_data = user_in.dict(exclude={"password", "organizations", "projects"}, skip_defaults=True)
    for field in user_data:
        if field in update_data:
            setattr(user, field, update_data[field])

    if user_in.organizations:
        roles = []
        for role in user_in.organizations:
            roles.append(await create_or_update_organization_role(db_session=db_session, user=user, role_in=role))
        user.organizations = roles

    if user_in.projects:
        # we reset the default value for all user projects
        for user_project in user.projects:
            user_project.default = False

        projects = []
        for user_project in user_in.projects:
            projects.append(
                await create_or_update_project_default(db_session=db_session, user=user, user_project_in=user_project)
            )
        user.projects = projects

    if experimental_features := user_in.experimental_features:
        user.experimental_features = experimental_features

    await db_session.commit()
    return user


async def get_current_user(request: Request) -> FarmbaseUser:
    """Attempts to get the current user depending on the configured authentication provider."""
    if FARMBASE_AUTHENTICATION_PROVIDER_SLUG:
        auth_plugin = plugins.get(FARMBASE_AUTHENTICATION_PROVIDER_SLUG)
        user_email = auth_plugin.get_current_user(request)
    else:
        log.debug("No authentication provider. Default user will be used")
        user_email = FARMBASE_AUTHENTICATION_DEFAULT_USER

    if not user_email:
        log.exception(
            f"Unable to determine user email based on configured auth provider or no default auth user email defined. Provider: {FARMBASE_AUTHENTICATION_PROVIDER_SLUG}"
        )
        raise InvalidCredentialException

    return await get_or_create(
        db_session=request.state.db,
        organization=request.state.organization,
        user_in=UserRegister(email=user_email),
    )


CurrentUser = Annotated[FarmbaseUser, Depends(get_current_user)]


async def get_current_role(request: Request, current_user: FarmbaseUser = Depends(get_current_user)) -> UserRoles:
    """Attempts to get the current user depending on the configured authentication provider."""
    return await current_user.get_organization_role(organization_slug=request.state.organization)
