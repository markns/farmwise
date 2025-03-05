from typing import *

from pydantic import BaseModel, Field


class ValidationError(BaseModel):
    """
    ValidationError model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    loc: List[Union[str, int]] = Field(validation_alias="loc")

    msg: str = Field(validation_alias="msg")

    type: str = Field(validation_alias="type")
