from fastapi import APIRouter

from farmbase.api2.routes import crop_varieties, farms, fields, gaez, items, login, private, users, utils
from farmbase.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router, include_in_schema=False)
api_router.include_router(users.router)
api_router.include_router(utils.router, include_in_schema=False)
api_router.include_router(items.router)
api_router.include_router(farms.router)
api_router.include_router(fields.router)
api_router.include_router(crop_varieties.router)
api_router.include_router(gaez.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
