"""Farmwise Agent Toolkit."""
from typing import List, Optional

from pydantic import PrivateAttr

from ..api import FarmwiseAPI
from ..configuration import Configuration, is_tool_allowed
from ..tools import tools
from .tool import FarmwiseTool


class FarmwiseAgentToolkit:
    _tools: List = PrivateAttr(default=[])

    def __init__(self,
                 secret_key: str, configuration: Optional[Configuration] = None
    ):
        super().__init__()

        context = configuration.get("context") if configuration else None

        farmwise_api = FarmwiseAPI(secret_key=secret_key, context=context)

        filtered_tools = [
            tool for tool in tools if is_tool_allowed(tool, configuration)
        ]

        self._tools = [
            FarmwiseTool(
                name=tool["method"],
                description=tool["description"],
                method=tool["method"],
                farmwise_api=farmwise_api,
                args_schema=tool.get("args_schema", None),
            )
            for tool in filtered_tools
        ]

    def get_tools(self) -> List:
        """Get the tools in the toolkit."""
        return self._tools
