"""
This tool allows agents to interact with the Farmwise API.
"""

from __future__ import annotations

from typing import Any, Optional, Type

from langchain.tools import BaseTool
from pydantic import BaseModel

from ..api import FarmwiseAPI


class FarmwiseTool(BaseTool):
    """Tool for interacting with the Farmwise API."""

    farmwise_api: FarmwiseAPI
    method: str
    name: str = ""
    description: str = ""
    args_schema: Optional[Type[BaseModel]] = None

    def _run(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """Use the Farmwise API to run an operation."""
        return self.farmwise_api.run(self.method, *args, **kwargs)
