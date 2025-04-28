from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette.responses import JSONResponse

from farmbase.auth.views import auth_router
from farmbase.models import OrganizationSlug
from farmbase.organization.views import router as organization_router
from farmbase.project.views import router as project_router


class ErrorMessage(BaseModel):
    msg: str


class ErrorResponse(BaseModel):
    detail: Optional[List[ErrorMessage]]


api_router = APIRouter(
    default_response_class=JSONResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)

# WARNING: Don't use this unless you want unauthenticated routes
authenticated_api_router = APIRouter()


def get_organization_path(organization: OrganizationSlug):
    pass


api_router.include_router(auth_router, prefix="/{organization}/auth", tags=["auth"])

# NOTE: All api routes should be authenticated by default
authenticated_api_router.include_router(organization_router, prefix="/organizations", tags=["organizations"])

authenticated_organization_api_router = APIRouter(
    prefix="/{organization}", dependencies=[Depends(get_organization_path)]
)

authenticated_organization_api_router.include_router(project_router, prefix="/projects", tags=["projects"])
