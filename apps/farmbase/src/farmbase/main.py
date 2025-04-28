import logging
from contextvars import ContextVar
from os import path
from typing import Final, Optional

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

# from sentry_asgi import SentryMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.gzip import GZipMiddleware
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from .api import api_router
from .config import (
    STATIC_DIR,
)
from .logging_config import configure_logging
from .rate_limiter import limiter

log = logging.getLogger(__name__)

# we configure the logging level and format
configure_logging()


async def not_found(request, exc):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": [{"msg": "Not Found."}]})


exception_handlers = {404: not_found}

# we create the ASGI for the app
app = FastAPI(exception_handlers=exception_handlers, openapi_url="")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# we create the ASGI for the frontend
frontend = FastAPI(openapi_url="")
frontend.add_middleware(GZipMiddleware, minimum_size=1000)


@frontend.middleware("http")
async def default_page(request, call_next):
    response = await call_next(request)
    if response.status_code == 404:
        if STATIC_DIR:
            return FileResponse(path.join(STATIC_DIR, "index.html"))
    return response


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


api = FastAPI(
    title="FarmBase",
    description="Welcome to FarmBase's API documentation! Here you will able to discover all of the ways you "
    "can interact with the FarmBase API.",
    root_path="/api/v1",
    docs_url=None,
    openapi_url="/docs/openapi.json",
    redoc_url="/docs",
    generate_unique_id_function=custom_generate_unique_id,
    separate_input_output_schemas=False,
)
api.add_middleware(GZipMiddleware, minimum_size=1000)

REQUEST_ID_CTX_KEY: Final[str] = "request_id"
_request_id_ctx_var: ContextVar[Optional[str]] = ContextVar(REQUEST_ID_CTX_KEY, default=None)


def get_request_id() -> Optional[str]:
    return _request_id_ctx_var.get()


# app.include_router(api_router, prefix=settings.API_V1_STR)

api.include_router(api_router)

# we mount the frontend and app
if STATIC_DIR and path.isdir(STATIC_DIR):
    frontend.mount("/", StaticFiles(directory=STATIC_DIR), name="app")

app.mount("/api/v1", app=api)
app.mount("/", app=frontend)
