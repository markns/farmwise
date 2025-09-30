from dataclasses import dataclass

from agents import RunContextWrapper, function_tool
from pywa.types import FlowButton

from farmwise.context import UserContext
from farmwise.whatsapp.flows.courses.courses import load_courses


@dataclass
class AvailableCourse:
    description: str
    flow_button: FlowButton


@function_tool
async def available_courses(_: RunContextWrapper[UserContext]) -> list[AvailableCourse]:
    """
    Fetches the list of available courses.

    This function retrieves all the courses and returns them in the form of
    `AvailableCourse` objects. Each course object includes a description and a flow button.

    Args:
        _: RunContextWrapper[UserContext]: The runtime context wrapper
            containing user-specific context and execution environment.

    Returns:
        list[AvailableCourse]: A list of courses represented as
            `AvailableCourse` objects, where each includes a course
            description and a flow button.
    """
    courses = load_courses()

    return [AvailableCourse(description=c.description, flow_button=c.flow_button()) for c in courses]
