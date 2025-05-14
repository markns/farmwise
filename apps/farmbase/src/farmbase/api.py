from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette.responses import JSONResponse

from farmbase.auth.service import get_current_user
from farmbase.auth.views import auth_router, user_router
from farmbase.contact.views import router as contact_router
from farmbase.data.crops.views import router as crops_router
from farmbase.data.gaez.views import router as gaez_router
from farmbase.messages.views import router as messages_router
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

authenticated_api_router.include_router(gaez_router, prefix="/gaez", tags=["gaez"])
authenticated_api_router.include_router(crops_router, prefix="/crop-varieties", tags=["crop-varieties"])


def get_organization_path(organization: OrganizationSlug):
    pass


api_router.include_router(auth_router, prefix="/{organization}/auth", tags=["auth"])

# NOTE: All api routes should be authenticated by default
authenticated_api_router.include_router(organization_router, prefix="/organizations", tags=["organizations"])

authenticated_organization_api_router = APIRouter(
    prefix="/{organization}", dependencies=[Depends(get_organization_path)]
)

authenticated_organization_api_router.include_router(project_router, prefix="/projects", tags=["projects"])
authenticated_organization_api_router.include_router(contact_router, prefix="/contacts", tags=["contacts"])

authenticated_organization_api_router.include_router(user_router, prefix="/users", tags=["users"])
authenticated_organization_api_router.include_router(messages_router, prefix="/messages", tags=["messages"])


@api_router.get("/healthcheck", include_in_schema=False)
def healthcheck():
    return {"status": "ok"}


api_router.include_router(authenticated_organization_api_router, dependencies=[Depends(get_current_user)])

api_router.include_router(
    authenticated_api_router,
    dependencies=[Depends(get_current_user)],
)
