from typing import Callable

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from loguru import logger

from farmbase.exceptions.exceptions import (
    AuthenticationFailed,
    EntityAlreadyExistsError,
    EntityDoesNotExistError,
    FarmBaseApiError,
    InvalidOperationError,
    InvalidTokenError,
    ServiceError,
)


def create_exception_handler(
    status_code: int, initial_detail: str
) -> Callable[[Request, FarmBaseApiError], JSONResponse]:
    detail = {"message": initial_detail}  # Using a dictionary to hold the detail

    async def exception_handler(_: Request, exc: FarmBaseApiError) -> JSONResponse:
        if exc.message:
            detail["message"] = exc.message

        if exc.name:
            detail["message"] = f"{detail['message']}"  #  [{exc.name}]

        logger.error(exc)
        return JSONResponse(status_code=status_code, content={"detail": detail["message"]})

    return exception_handler


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        exc_class_or_status_code=EntityAlreadyExistsError,
        handler=create_exception_handler(status.HTTP_409_CONFLICT, "Entity does not exist."),
    )
    app.add_exception_handler(
        exc_class_or_status_code=EntityDoesNotExistError,
        handler=create_exception_handler(status.HTTP_404_NOT_FOUND, "Entity does not exist."),
    )

    app.add_exception_handler(
        exc_class_or_status_code=InvalidOperationError,
        handler=create_exception_handler(status.HTTP_400_BAD_REQUEST, "Can't perform the operation."),
    )

    # app.add_exception_handler(
    #     exc_class_or_status_code=IntegrityError,
    #     handler=create_exception_handler(
    #         status.HTTP_400_BAD_REQUEST, "Can't process the request due to integrity error."
    #     ),
    # )
    #
    # app.add_exception_handler(
    #     exc_class_or_status_code=DataError,
    #     handler=create_exception_handler(status.HTTP_400_BAD_REQUEST, "Data can't be processed, check the input."),
    # )

    app.add_exception_handler(
        exc_class_or_status_code=AuthenticationFailed,
        handler=create_exception_handler(
            status.HTTP_401_UNAUTHORIZED,
            "Authentication failed due to invalid credentials.",
        ),
    )

    app.add_exception_handler(
        exc_class_or_status_code=InvalidTokenError,
        handler=create_exception_handler(status.HTTP_401_UNAUTHORIZED, "Invalid token, please re-authenticate again."),
    )

    app.add_exception_handler(
        exc_class_or_status_code=ServiceError,
        handler=create_exception_handler(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "A service seems to be down, try again later.",
        ),
    )
