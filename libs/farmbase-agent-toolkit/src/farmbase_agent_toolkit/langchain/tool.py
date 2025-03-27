"""
This tool allows agents to interact with the Farmwise API.
"""

from __future__ import annotations

from typing import Any, Optional

from langchain.tools import BaseTool
from langchain_core.tools import ArgsSchema

from ..api import FarmbaseAPI


class FarmbaseTool(BaseTool):
    """Tool for interacting with the Farmbase API."""

    farmbase_api: FarmbaseAPI
    name: str = ""
    description: str = ""
    args_schema: Optional[ArgsSchema] = None

    def _run(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """Use the Farmwise API to run an operation."""
        return self.farmbase_api.run(self.name, *args, **kwargs)
