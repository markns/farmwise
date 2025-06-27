from enum import Enum


class RunItemStreamEventName(str, Enum):
    MESSAGE_OUTPUT_CREATED = "message_output_created"
    HANDOFF_REQUESTED = "handoff_requested"
    HANDOFF_OCCURED = "handoff_occured"  # noqa - typo in source
    TOOL_CALLED = "tool_called"
    TOOL_OUTPUT = "tool_output"
    REASONING_ITEM_CREATED = "reasoning_item_created"
    MCP_APPROVAL_REQUESTED = "mcp_approval_requested"
    MCP_LIST_TOOLS = "mcp_list_tools"