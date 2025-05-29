from temporalio import workflow

# Always pass through external modules to the sandbox that you know are safe for
# workflow use
with workflow.unsafe.imports_passed_through():
    from pydantic import BaseModel


# TODO: Maybe can use ContactRead here?
class SimpleContact(BaseModel):
    id: int
    phone_number: str
    name: str
    location: str
