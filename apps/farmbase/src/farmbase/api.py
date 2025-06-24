from typing import List, Optional

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import BaseModel
from starlette.responses import JSONResponse

from farmbase.auth import authenticate_user_or_machine
from farmbase.chatstate.views import router as chatstate_router
from farmbase.commodity.views import router as commodity_router
from farmbase.contact.views import router as contact_router
from farmbase.data.crops.views import router as crops_router
from farmbase.data.gaez.views import router as gaez_router
from farmbase.farm.note.views import router as note_router
from farmbase.farm.views import router as farm_router
from farmbase.market.views import router as market_router
from farmbase.models import OrganizationSlug
from farmbase.organization.views import router as organization_router
from farmbase.agronomy.views import router as agronomy_router
from farmbase.products.views import router as products_router
from farmbase.runresult.views import router as runresult_router
from farmbase.market.views import price_router

class ErrorMessage(BaseModel):
    msg: str


class ErrorResponse(BaseModel):
    detail: Optional[List[ErrorMessage]]

# WARNING: Don't use this unless you want unauthenticated routes
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

authenticated_api_router = APIRouter(dependencies=[Depends(authenticate_user_or_machine)])


def get_organization_path(organization: OrganizationSlug): ...


authenticated_organization_api_router = APIRouter(
    prefix="/{organization}", dependencies=[Depends(get_organization_path), Depends(authenticate_user_or_machine)]
)


authenticated_api_router.include_router(gaez_router, prefix="/gaez", tags=["gaez"])
authenticated_api_router.include_router(crops_router, prefix="/crop-varieties", tags=["crop-varieties"])
authenticated_api_router.include_router(agronomy_router, prefix="/agronomy", tags=["agronomy"])

# NOTE: All api routes should be authenticated by default
authenticated_api_router.include_router(organization_router, prefix="/organizations", tags=["organizations"])

authenticated_organization_api_router.include_router(contact_router, prefix="/contacts", tags=["contacts"])

authenticated_organization_api_router.include_router(chatstate_router, prefix="/chatstate", tags=["chatstate"])
authenticated_organization_api_router.include_router(runresult_router, prefix="/runresult", tags=["runresult"])

authenticated_organization_api_router.include_router(products_router, prefix="/products", tags=["products"])
authenticated_organization_api_router.include_router(farm_router, prefix="/farms", tags=["farms"])
authenticated_organization_api_router.include_router(note_router, prefix="/notes", tags=["notes"])
authenticated_api_router.include_router(commodity_router, prefix="/commodities", tags=["commodities"])
authenticated_api_router.include_router(market_router, prefix="/markets", tags=["markets"])
authenticated_api_router.include_router(price_router, prefix="/market_prices", tags=["market_prices"])


@api_router.get("/healthcheck", include_in_schema=False)
def healthcheck():
    return {"status": "ok"}


api_router.include_router(authenticated_organization_api_router)

api_router.include_router(authenticated_api_router)
