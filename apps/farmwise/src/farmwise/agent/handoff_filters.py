import json

from agents import (
    HandoffInputData,
    TResponseInputItem,
)
from loguru import logger

from farmwise.schema import TextResponse


def remove_whatsapp_interactivity(handoff_input_data: HandoffInputData) -> HandoffInputData:
    history = handoff_input_data.input_history

    filtered_history = _whatsapp_interactivity_from_input(history) if isinstance(history, tuple) else history

    return HandoffInputData(
        input_history=filtered_history,
        pre_handoff_items=handoff_input_data.pre_handoff_items,
        new_items=handoff_input_data.new_items,
    )


def _whatsapp_interactivity_from_input(
    items: tuple[TResponseInputItem, ...],
) -> tuple[TResponseInputItem, ...]:
    filtered_items: list[TResponseInputItem] = []

    for item in items:
        role = item.get("role")
        if role == "assistant":
            # noinspection PyBroadException
            try:
                original = item["content"][0]["text"]
                response = TextResponse.model_validate(json.loads(original))
                item["content"][0]["text"] = response.content
                logger.debug(f"removed whatsapp interactivity from {original} -> {item}")
            except Exception:
                pass
        filtered_items.append(item)
    return tuple(filtered_items)


def remove_images(handoff_input_data: HandoffInputData) -> HandoffInputData:
    def _remove_images(
        items: tuple[TResponseInputItem, ...],
    ) -> tuple[TResponseInputItem, ...]:
        for item in items:
            if "content" in item and isinstance(item["content"], list):
                item["content"] = [c for c in item["content"] if "image_url" not in c]
        return items

    history = handoff_input_data.input_history
    filtered_history = _remove_images(history) if isinstance(history, tuple) else history

    return HandoffInputData(
        input_history=filtered_history,
        pre_handoff_items=handoff_input_data.pre_handoff_items,
        new_items=handoff_input_data.new_items,
    )
