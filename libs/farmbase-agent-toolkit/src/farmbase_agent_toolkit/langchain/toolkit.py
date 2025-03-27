"""Farmwise Agent Toolkit."""

from typing import List, Optional

from pydantic import PrivateAttr

from ..api import FarmbaseAPI
from ..configuration import Configuration
from .tool import FarmbaseTool


class FarmbaseAgentToolkit:
    _tools: List = PrivateAttr(default=[])

    def __init__(self, secret_key: str, configuration: Optional[Configuration] = None):
        super().__init__()

        context = configuration.get("context") if configuration else None

        farmbase_api = FarmbaseAPI(secret_key=secret_key, context=context)

        # filtered_tools = [tool for tool in tools if is_tool_allowed(tool, configuration)]

        tool_defs = []
        # tool_defs = get_tool_defs(
        #     [
        #         farmbase_api.create_farm,
        #         farmbase_api.create_field,
        #         farmbase_api.do_nothing,
        #     ],
        #     strict=True,
        # )

        print(tool_defs)
        self._tools = [
            FarmbaseTool(
                name=tool["function"]["name"],
                description=tool["function"]["description"],
                farmbase_api=farmbase_api,
                args_schema=tool["function"]["parameters"],
            )
            for tool in tool_defs
        ]

    def get_tools(self) -> List:
        """Get the tools in the toolkit."""
        return self._tools
