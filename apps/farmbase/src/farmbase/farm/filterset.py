from pydantic import Field
from sqlalchemy_filterset import (
    Filter,
    JoinStrategy,
    OrderingField,
    OrderingFilter,
    SearchFilter,
)

from ..contact.models import Contact
from ..database.core import BaseFilterSet
from ..models import PaginationParams
from .models import Farm, FarmContact


class FarmFilterSet(BaseFilterSet[Farm]):
    farm_name = SearchFilter(Farm.farm_name)
    address = SearchFilter(Farm.address)
    ordering = OrderingFilter(
        id=OrderingField(Farm.id),
        farm_name=OrderingField(Farm.farm_name),
        date_registered=OrderingField(Farm.date_registered),
    )


class FarmQueryParams(PaginationParams):
    farm_name: str | None = Field(None)
    address: str | None = Field(None)


class FarmContactFilterSet(BaseFilterSet[FarmContact]):
    role = SearchFilter(FarmContact.role)
    farm_id = Filter(FarmContact.farm_id)
    contact_id = Filter(FarmContact.contact_id)
    contact_name = Filter(
        Contact.name,
        strategy=JoinStrategy(
            Contact,
            FarmContact.contact_id == Contact.id,
        ),
    )
    ordering = OrderingFilter(
        id=OrderingField(FarmContact.id),
        role=OrderingField(FarmContact.role),
    )


class FarmContactQueryParams(PaginationParams):
    role: str | None = Field(None)
    farm_id: int | None = Field(None)
    contact_id: int | None = Field(None)
    contact_name: str | None = Field(None)