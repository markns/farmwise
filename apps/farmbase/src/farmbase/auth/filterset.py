from pydantic import Field
from sqlalchemy_filterset import (
    OrderingField,
    OrderingFilter,
    SearchFilter,
)

from ..database.core import BaseFilterSet
from ..models import PaginationParams
from .models import FarmbaseUser


class UserFilterSet(BaseFilterSet[FarmbaseUser]):
    email = SearchFilter(FarmbaseUser.email)

    ordering = OrderingFilter(
        id=OrderingField(FarmbaseUser.id),
        email=OrderingField(FarmbaseUser.email),
    )


class UserQueryParams(PaginationParams):
    email: str | None = Field(None)
