from typing import *

from pydantic import BaseModel, Field

from .ValidationError import ValidationError


class HTTPValidationError(BaseModel):
    """
    HTTPValidationError model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    detail: Optional[List[Optional[ValidationError]]] = Field(validation_alias="detail", default=None)
