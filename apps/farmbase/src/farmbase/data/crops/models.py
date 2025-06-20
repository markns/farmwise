from typing import List

from pydantic import BaseModel


class CropVarietyResponse(BaseModel):
    variety: str
    producer: str
    # website: str
    description: str
    maturity_months: str
    yield_tons_ha: str
    min_altitude_masl: float
    max_altitude_masl: float
    maturity_category: str


class CropVarietiesResponse(BaseModel):
    crop: str
    varieties: List[CropVarietyResponse]
