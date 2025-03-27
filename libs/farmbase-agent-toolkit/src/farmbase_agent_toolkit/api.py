"""Util that calls the Farmwise API."""

from __future__ import annotations

from typing import Optional, Tuple, List
from uuid import UUID

from farmbase_client import AuthenticatedClient as FarmbaseClient
from farmbase_client.api.farms import farms_create_farm
from farmbase_client.api.fields import fields_create_field
from farmbase_client.models import FarmCreate, FieldCreate
from geojson_pydantic import LineString
from pydantic import BaseModel

from .configuration import Context

# from .functions import (
# create_animal,
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
# )


class FarmbaseAPI(BaseModel):
    """Wrapper for Farmbase API"""

    _context: Context
    url: str = "http://127.0.0.1:8000/"

    def __init__(self, secret_key: str, context: Optional[Context]):
        super().__init__()

        self._context = context if context is not None else Context()
        self._secret_key = secret_key
        # stripe.api_key = secret_key
        # stripe.set_app_info(
        #     "stripe-agent-toolkit-python",
        #     version="0.2.0",
        #     url="https://github.com/stripe/agent-toolkit",
        # )

    def run(self, method: str, *args, **kwargs) -> str:
        print(method, args, kwargs)
        try:
            return getattr(self, method)(*args, **kwargs)
        except AttributeError:
            raise ValueError("Invalid method " + method)

    def create_farm(self, name: str, location: str):
        """
        This tool creates a new farm in Farmbase
        """
        # TODO: read httpx client config docs: https://www.python-httpx.org/advanced/clients/
        with FarmbaseClient(base_url=self.url, token=self._secret_key) as client:
            response = farms_create_farm.sync(client=client, body=FarmCreate(name=name, location=location))
            return response.model_dump_json()

    def create_field(self, farm_id: str, name: str, boundary: List[Tuple[float, float]]):
        """
        This tool creates a new field in Farmbase

        Args:
            farm_id: The ID of the farm that the field belongs to.
            name: the name of the field.
            boundary: the boundary of the field as a list of [long, lat] coordinates.

        """

        with FarmbaseClient(base_url=self.url, token=self._secret_key) as client:
            response = fields_create_field.sync(
                farm_id=UUID(farm_id),
                client=client,
                body=FieldCreate(name=name, boundary=LineString(type="LineString", coordinates=boundary)),
            )

            return response.model_dump_json()

    def do_nothing(self):
        pass
