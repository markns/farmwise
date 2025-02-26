"""Util that calls the Farmwise API."""

from __future__ import annotations

import json
from typing import Optional

from pydantic import BaseModel

from .configuration import Context
from .functions import (
    create_animal,
    # list_customers,
    # create_product,
    # list_products,
    # create_price,
    # list_prices,
    # create_payment_link,
    # create_invoice,
    # create_invoice_item,
    # finalize_invoice,
    # retrieve_balance,
    # create_refund,
)


class FarmwiseAPI(BaseModel):
    """ "Wrapper for Farmwise API"""

    _context: Context
    url: str = "http://127.0.0.1:8000/"

    def __init__(self, secret_key: str, context: Optional[Context]):
        super().__init__()

        self._context = context if context is not None else Context()

        # stripe.api_key = secret_key
        # stripe.set_app_info(
        #     "stripe-agent-toolkit-python",
        #     version="0.2.0",
        #     url="https://github.com/stripe/agent-toolkit",
        # )


    def run(self, method: str, *args, **kwargs) -> str:
        if method == "create_animal":
            return json.dumps(create_animal(self._context, **kwargs))
        else:
            raise ValueError("Invalid method " + method)
