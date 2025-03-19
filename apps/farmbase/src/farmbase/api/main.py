from fastapi import APIRouter

from farmbase.api.routes import items, login, private, users, utils, farms, fields
from farmbase.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router, include_in_schema=False)
api_router.include_router(users.router)
api_router.include_router(utils.router, include_in_schema=False)
api_router.include_router(items.router)
api_router.include_router(farms.router)
api_router.include_router(fields.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
