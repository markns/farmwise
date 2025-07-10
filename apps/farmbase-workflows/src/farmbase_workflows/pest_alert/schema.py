from temporalio import workflow

from farmbase_workflows.whatsapp.schema import SimpleContact

# Always pass through external modules to the sandbox that you know are safe for
# workflow use
with workflow.unsafe.imports_passed_through():
    from pydantic import BaseModel


class AlertDetails(BaseModel):
    note_id: int
    note_text: str
    farm_id: int
    farm_name: str
    note_location: str
    tags: str | None = None
    created_at: str


class AlertMessage(BaseModel):
    summary: str
    actions: list[str]


class FarmWithContacts(BaseModel):
    farm_id: int
    farm_name: str
    distance_km: float
    contacts: list[SimpleContact]  # List of contact info dicts
