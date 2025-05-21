from pydantic import Field
from sqlalchemy_filterset import (
    OrderingField,
    OrderingFilter,
    SearchFilter,
)

from ..database.core import BaseFilterSet
from ..models import PaginationParams
from .models import Organization


class OrganizationFilterSet(BaseFilterSet[Organization]):
    name = SearchFilter(Organization.name)
    ordering = OrderingFilter(
        id=OrderingField(Organization.id),
        name=OrderingField(Organization.name),
    )


class OrganizationQueryParams(PaginationParams):
    name: str | None = Field(None)
