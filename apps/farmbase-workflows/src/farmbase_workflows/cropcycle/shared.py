from temporalio import workflow

CROP_CYCLE_TASK_QUEUE = "CROP_CYCLE_TASK_QUEUE"

# Always pass through external modules to the sandbox that you know are safe for
# workflow use
with workflow.unsafe.imports_passed_through():
    from pydantic import BaseModel


class CropCycleEvent(BaseModel):
    """Represents a single crop cycle event"""

    event_type: str
    event_category: str
    title: str
    start_day: int
    end_day: int
    identifier: str
    image_list: dict | None = None
    prevent_pathogens: list | None = None
    nutshell: str
    description: str


class CropCycleWorkflowInput(BaseModel):
    """Input parameters for the crop cycle workflow"""

    contact_id: int
    contact_phone: str
    contact_name: str
    contact_location: str | None = None
    planting_date: str  # ISO format date string
    events_data: list[dict]  # List of event dictionaries that will be converted to DataFrame
