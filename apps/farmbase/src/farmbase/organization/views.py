from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import select

from farmbase.database.core import DbSession

from .filterset import OrganizationFilterSet, OrganizationQueryParams
from .models import (
    Organization,
    OrganizationPagination,
)

router = APIRouter()


@router.get("", response_model=OrganizationPagination)
async def get_organizations(db_session: DbSession, query_params: Annotated[OrganizationQueryParams, Query()]):
    """Get all organizations."""
    stmt = select(Organization)
    filter_set = OrganizationFilterSet(db_session, stmt)
    params_d = query_params.model_dump(exclude_none=True)
    total = await filter_set.count(params_d)
    organizations = await filter_set.filter(params_d)
    return OrganizationPagination(
        items=organizations,
        items_per_page=query_params.items_per_page,
        page=query_params.page,
        total=total,
    )


#
# @router.post(
#     "",
#     response_model=OrganizationRead,
# )
# async def create_organization(
#     db_session: DbSession,
#     organization_in: OrganizationCreate,
#     current_user: CurrentUser,
# ):
#     """Create a new organization."""
#     if not organization_in.name:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=[{"msg": "An organization name is required."}],
#         )
#     organization = await get_by_name(db_session=db_session, name=organization_in.name)
#     if organization:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail=[{"msg": "An organization with this name already exists."}],
#         )
#     if organization_in.id and get(db_session=db_session, organization_id=organization_in.id):
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail=[{"msg": "An organization with this id already exists."}],
#         )
#     slug = slugify(organization_in.name, separator="_")
#     if await get_by_slug(db_session=db_session, slug=slug):
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail=[{"msg": "An organization with this slug already exists."}],
#         )
#     # we create the organization
#     organization = await create(db_session=db_session, organization_in=organization_in)
#
#     # we add the creator as organization owner
#     # await add_user(db_session=db_session, organization=organization, user=current_user, role=UserRoles.owner)
#
#     # we create the default project
#     project_in = ProjectCreate(
#         name="default",
#         default=True,
#         description="Default Farmbase project.",
#         organization=organization,
#     )
#     project = await project_service.create(db_session=db_session, project_in=project_in)
#
#     # we initialize the default project
#     await project_flows.project_init_flow(
#         project_id=project.id, organization_slug=organization.slug, db_session=db_session
#     )
#
#     return organization
#
#
# @router.get("/{organization_id}", response_model=OrganizationRead)
# async def get_organization(db_session: DbSession, organization_id: PrimaryKey):
#     """Get an organization."""
#     organization = await get(db_session=db_session, organization_id=organization_id)
#     if not organization:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=[{"msg": "An organization with this id does not exist."}],
#         )
#     return organization
