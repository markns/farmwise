from agents import (
    HandoffCallItem,
    HandoffOutputItem,
    MessageOutputItem,
    ReasoningItem,
    ToolCallItem,
    ToolCallOutputItem,
)
from farmbase.message.models import RunItem
from farmbase_client import models


def get_run_item_model(item: RunItem):
    match item:
        case MessageOutputItem(agent=agent, raw_item=raw_item):
            return models.MessageOutputItem(
                agent=agents_dict[agent.name],
                content=raw_item.content[0].text,
                raw_item=[r.model_dump() for r in raw_item.content],
            )

        case HandoffCallItem(agent=agent, raw_item=raw_item):
            return models.HandoffCallItem(agent=agents_dict[agent.name], raw_item=raw_item.model_dump())

        case HandoffOutputItem(source_agent=src, target_agent=tgt, raw_item=raw_item):
            return models.HandoffOutputItem(
                source_agent=agents_dict[src.name], target_agent=agents_dict[tgt.name], raw_item=raw_item
            )

        case ToolCallItem(agent=agent, raw_item=raw_item):
            return models.ToolCallItem(
                agent=agents_dict[agent.name],
                # tool_name=raw_item.name,
                raw_item=raw_item.model_dump(),
            )

        case ToolCallOutputItem(agent=agent, raw_item=raw_item, output=output):
            return models.ToolCallOutputItem(agent=agents_dict[agent.name], raw_item=raw_item, output=output)

        case ReasoningItem(agent=agent, raw_item=raw_item):
            return models.ReasoningItem(agent=agents_dict[agent.name], raw_item=raw_item)

        # Fallback – should not happen if the hierarchy is complete
        case _:
            raise TypeError(f"Unrecognised RunItem subclass: {type(item).__name__}")
