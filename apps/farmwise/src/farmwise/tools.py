from __future__ import annotations as _annotations

from agents import (
    RunContextWrapper,
    function_tool,
)

from farmwise.context import UserContext


@function_tool(name_override="faq_lookup_tool", description_override="Lookup frequently asked questions.")
async def faq_lookup_tool(question: str) -> str:
    if "bag" in question or "baggage" in question:
        return (
            "You are allowed to bring one bag on the plane. "
            "It must be under 50 pounds and 22 inches x 14 inches x 9 inches."
        )
    elif "seats" in question or "plane" in question:
        return (
            "There are 120 seats on the plane. "
            "There are 22 business class seats and 98 economy seats. "
            "Exit rows are rows 4 and 16. "
            "Rows 5-8 are Economy Plus, with extra legroom. "
        )
    elif "wifi" in question:
        return "We have free wifi on the plane, join Airline-Wifi"
    return "I'm sorry, I don't know the answer to that question."


@function_tool
async def update_seat(context: RunContextWrapper[UserContext], confirmation_number: str, new_seat: str) -> str:
    """
    Update the seat for a given confirmation number.

    Args:
        confirmation_number: The confirmation number for the flight.
        new_seat: The new seat to update to.
    """
    # Update the context based on the customer's input
    context.context.confirmation_number = confirmation_number
    context.context.seat_number = new_seat
    # Ensure that the flight number has been set by the incoming handoff
    assert context.context.flight_number is not None, "Flight number is required"
    return f"Updated seat to {new_seat} for confirmation number {confirmation_number}"
