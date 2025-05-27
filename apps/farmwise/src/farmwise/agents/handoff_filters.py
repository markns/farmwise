import json

from agents import (
    HandoffInputData,
    TResponseInputItem,
)
from farmwise_schema.schema import WhatsAppResponse
from loguru import logger


def remove_whatsapp_interactivity(handoff_input_data: HandoffInputData) -> HandoffInputData:
    """Filters out all tool items: file search, web search and function calls+output."""

    history = handoff_input_data.input_history

    filtered_history = whatsapp_interactivity_from_input(history) if isinstance(history, tuple) else history
    # filtered_pre_handoff_items = _remove_whatsapp_interactivity_from_items(handoff_input_data.pre_handoff_items)
    # filtered_new_items = _remove_whatsapp_interactivity_from_items(new_items)

    return HandoffInputData(
        input_history=filtered_history,
        pre_handoff_items=handoff_input_data.pre_handoff_items,
        new_items=handoff_input_data.new_items,
    )


#
# def _remove_whatsapp_interactivity_from_items(items: tuple[RunItem, ...]) -> tuple[RunItem, ...]:
#     filtered_items = []
#     for item in items:
#         if (
#             isinstance(item, HandoffCallItem)
#             or isinstance(item, HandoffOutputItem)
#             or isinstance(item, ToolCallItem)
#             or isinstance(item, ToolCallOutputItem)
#         ):
#             continue
#         filtered_items.append(item)
#     return tuple(filtered_items)


def whatsapp_interactivity_from_input(
    items: tuple[TResponseInputItem, ...],
) -> tuple[TResponseInputItem, ...]:
    filtered_items: list[TResponseInputItem] = []

    for item in items:
        role = item.get("role")
        if role == "assistant":
            # noinspection PyBroadException
            try:
                original = item["content"][0]["text"]
                response = WhatsAppResponse.model_validate(json.loads(original))
                item["content"][0]["text"] = response.content
                logger.debug(f"removed whatsapp interactivity from {original} -> {item}")
            except Exception:
                pass
        filtered_items.append(item)
    return tuple(filtered_items)
