from temporalio import workflow


# Always pass through external modules to the sandbox that you know are safe for
# workflow use
with workflow.unsafe.imports_passed_through():
    from pydantic import BaseModel


class LocationQuery(BaseModel):
    location: str


class ForecastDetails(BaseModel):
    location: str
    country: str
    hourly_descriptions: list[str]


class ForecastSummary(BaseModel):
    location: str
    forecast: list[str]
