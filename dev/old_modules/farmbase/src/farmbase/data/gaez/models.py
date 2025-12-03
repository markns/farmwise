from pydantic import BaseModel


class SuitabilityIndexResponse(BaseModel):
    suitability_index: dict[str, int]
