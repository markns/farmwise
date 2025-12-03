from pydantic import Field
from sqlalchemy_filterset import (
    OrderingField,
    OrderingFilter,
    SearchFilter,
)

from ..database.core import BaseFilterSet
from ..models import PaginationParams
from .models import Contact


class ContactFilterSet(BaseFilterSet[Contact]):
    name = SearchFilter(Contact.name)

    ordering = OrderingFilter(
        id=OrderingField(Contact.id),
        name=OrderingField(Contact.name),
    )


class ContactQueryParams(PaginationParams):
    name: str | None = Field(None)
