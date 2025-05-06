from typing import List

from pydantic import BaseModel


class CropVarietyResponse(BaseModel):
    variety: str
    description: str
    max_yield: str


class CropVarietiesResponse(BaseModel):
    crop: str
    varieties: List[CropVarietyResponse]
