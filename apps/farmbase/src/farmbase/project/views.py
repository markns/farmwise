from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import ValidationError

from farmbase.auth.permissions import (
    PermissionsDependency,
    ProjectCreatePermission,
    ProjectUpdatePermission,
)
from farmbase.database.core import DbSession
from farmbase.database.service import CommonParameters, search_filter_sort_paginate
from farmbase.models import OrganizationSlug, PrimaryKey

from .flows import project_init_flow
from .models import (
    ProjectCreate,
    ProjectPagination,
    ProjectRead,
    ProjectUpdate,
)
from .service import create, delete, get, get_by_name, update

router = APIRouter()


@router.get("", response_model=ProjectPagination)
async def get_projects(common: CommonParameters):
    """Get all projects."""
    return await search_filter_sort_paginate(model="Project", **common)


@router.post(
    "",
    response_model=ProjectRead,
    summary="Create a new project.",
    dependencies=[Depends(PermissionsDependency([ProjectCreatePermission]))],
)
async def create_project(
    db_session: DbSession,
    organization: OrganizationSlug,
    project_in: ProjectCreate,
    background_tasks: BackgroundTasks,
):
    """Create a new project."""
    project = await get_by_name(db_session=db_session, name=project_in.name)
    if project:
        raise ValidationError.from_exception_data(
            "ProjectCreate",
            [
                {
                    "loc": ("name",),
                    "msg": "A project with this name already exists.",
                    "type": "value_error.already_exists",
                }
            ],
        )

    if project_in.id and await get(db_session=db_session, project_id=project_in.id):
        raise ValidationError.from_exception_data(
            "ProjectCreate",
            [
                {
                    "loc": ("id",),
                    "msg": "A project with this id already exists.",
                    "type": "value_error.already_exists",
                }
            ],
        )

    project = await create(db_session=db_session, project_in=project_in)
    await project_init_flow(project_id=project.id, organization_slug=organization)
    return project


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Get a project.",
)
async def get_project(db_session: DbSession, project_id: PrimaryKey):
    """Get a project."""
    project = await get(db_session=db_session, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A project with this id does not exist."}],
        )
    return project


@router.put(
    "/{project_id}",
    response_model=ProjectRead,
    dependencies=[Depends(PermissionsDependency([ProjectUpdatePermission]))],
)
async def update_project(
    db_session: DbSession,
    project_id: PrimaryKey,
    project_in: ProjectUpdate,
):
    """Update a project."""
    project = await get(db_session=db_session, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A project with this id does not exist."}],
        )
    project = await update(db_session=db_session, project=project, project_in=project_in)
    return project


@router.delete(
    "/{project_id}",
    response_model=None,
    dependencies=[Depends(PermissionsDependency([ProjectUpdatePermission]))],
)
async def delete_project(db_session: DbSession, project_id: PrimaryKey):
    """Delete a project."""
    project = await get(db_session=db_session, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A project with this id does not exist."}],
        )
    await delete(db_session=db_session, project_id=project_id)
