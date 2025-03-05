from datetime import datetime
from typing import *

from pydantic import BaseModel, Field

from .SexEnum import SexEnum


class Animal(BaseModel):
    """
    Animal model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    animal_type: str = Field(validation_alias="animal_type")

    birthdate: Optional[Union[datetime, None]] = Field(validation_alias="birthdate", default=None)

    is_castrated: Optional[Union[bool, None]] = Field(validation_alias="is_castrated", default=None)

    nickname: List[str] = Field(validation_alias="nickname")

    sex: SexEnum = Field(validation_alias="sex")
